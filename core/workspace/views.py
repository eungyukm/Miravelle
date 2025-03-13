import json
import logging
from django.http import StreamingHttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import MeshModel

import threading

# utils
from .meshy_utils import call_meshy_api  # Meshy API 호출 함수
from .azure_utils import AzureBlobUploader

# 로깅 설정
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

@login_required
def create_mesh_page(request):
    """3D 모델 생성 페이지 렌더링"""
    return render(request, "workspace/create_mesh.html")


@csrf_exempt
@login_required
def generate_mesh(request):
    """Mesh 생성 요청 & job_id 반환"""
    if request.method != "POST":
        return JsonResponse({"error": "Invalid method"}, status=405)

    try:
        data = json.loads(request.body)
        prompt = data.get("prompt")
        art_style = data.get("art_style", "realistic")

        response_data = call_meshy_api("/openapi/v2/text-to-3d", "POST", {
            "mode": "preview", "prompt": prompt, "art_style": art_style
        })

        if response_data and "result" in response_data:
            job_id = response_data["result"]
            MeshModel.objects.create(
                user=request.user, 
                job_id=job_id, 
                status="processing",
                create_prompt=prompt  # 프롬프트 정보 저장
            )
            return JsonResponse({"job_id": job_id, "message": "Mesh 생성 시작!"})

        return JsonResponse({"error": "API 요청 실패"}, status=500)
    except json.JSONDecodeError:
        return JsonResponse({"error": "잘못된 JSON 데이터"}, status=400)


@login_required
def stream_mesh_progress(request, mesh_id):
    """진행률 SSE(서버 전송 이벤트) 스트리밍"""
    def event_stream():
        response = call_meshy_api(f"/openapi/v2/text-to-3d/{mesh_id}/stream", stream=True)
        if not response:
            yield f"data: {json.dumps({'error': 'API 응답 없음'})}\n\n"
            return

        for line in response.iter_lines():
            if line.startswith(b"data:"):
                data = json.loads(line[5:])
                yield f"data: {json.dumps({'progress': data['progress'], 'status': data['status']})}\n\n"
                if data["status"] in ["SUCCEEDED", "FAILED"]:
                    break  # 성공 또는 실패하면 스트리밍 종료

    return StreamingHttpResponse(event_stream(), content_type="text/event-stream")

def upload_blob_in_thread(request, response: dict):    
    """Azure Blob Storage 업로드를 백그라운드에서 실행"""
    def upload_task():
        uploader = AzureBlobUploader()
        uploader.upload_meshy_assets(request, response)  # request 추가

    thread = threading.Thread(target=upload_task)
    thread.start()

@login_required
def get_mesh(request, mesh_id):
    """진행률 100% 후 썸네일 & 비디오 URL 반환"""
    mesh = get_object_or_404(MeshModel, job_id=mesh_id)
    response_data = call_meshy_api(f"/openapi/v2/text-to-3d/{mesh_id}")

    if not response_data:
        return JsonResponse({"error": "Mesh 정보를 가져올 수 없습니다."}, status=400)

    # API 응답에서 썸네일 & 비디오 URL 추출
    thumbnail_url = response_data.get("thumbnail_url")
    video_url = response_data.get("video_url")

    upload_blob_in_thread(request, response_data)

    return JsonResponse({
        "job_id": mesh.job_id,
        "status": mesh.status,
        "thumbnail_url": thumbnail_url,
        "video_url": video_url
    })

def refine_mesh(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            mesh_id = data.get("mesh_id")
            
            print(f"Received mesh_id: {mesh_id}")  # 값 확인용 로그

            if not mesh_id:
                return JsonResponse({"error": "mesh_id가 필요합니다."}, status=400)

            payload = {
                "mode": "refine",
                "preview_task_id": mesh_id,
                "enable_pbr": True,
            }

            # 메서드 및 엔드포인트 정의
            endpoint = "/openapi/v2/text-to-3d"
            method = "POST"

            # API 호출
            response = call_meshy_api(endpoint=endpoint, method=method, payload=payload)

            print(f"API Response: {response}")  # API 응답 확인용 로그

            # 응답 처리
            if response and "result" in response:
                job_id = response.get("result")
                return JsonResponse({"job_id": job_id}, status=200)
            else:
                return JsonResponse({"error": "API 호출 실패"}, status=400)

        except json.JSONDecodeError as e:
            print(f"JSON Decode Error: {e}")  # JSON 파싱 오류 로그 출력
            return JsonResponse({"error": "잘못된 JSON 형식입니다."}, status=400)
        except Exception as e:
            print(f"Unhandled Error: {e}")  # 기타 오류 로그 출력
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "POST 요청만 허용됩니다."}, status=405)

@login_required
def stream_refine_mesh_progress(request, mesh_id):
    """진행률 SSE(서버 전송 이벤트) 스트리밍"""
    def event_stream():
        response = call_meshy_api(f"/openapi/v2/text-to-3d/{mesh_id}/stream", stream=True)
        if not response:
            yield f"data: {json.dumps({'error': 'API 응답 없음'})}\n\n"
            return

        for line in response.iter_lines():
            if line.startswith(b"data:"):
                data = json.loads(line[5:])
                
                # 반환할 데이터 구성
                job_data = {
                    "job_id": data.get("id"),
                    "status": data.get("status"),
                    "thumbnail_url": data.get("thumbnail_url", ""),
                    "progress": data.get("progress", 0),
                    "started_at": data.get("started_at"),
                    "finished_at": data.get("finished_at"),
                    "task_error": (data.get("task_error") or {}).get("message", "")  # 수정된 부분
                }
                
                # 스트리밍 응답 반환
                yield f"data: {json.dumps(job_data)}\n\n"
                
                # 상태가 성공 또는 실패일 경우 스트리밍 종료
                if data["status"] in ["SUCCEEDED", "FAILED"]:
                    break

    # 스트리밍 반환
    return StreamingHttpResponse(event_stream(), content_type="text/event-stream")