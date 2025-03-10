import json
import logging
from django.http import StreamingHttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from sseclient import SSEClient
from .models import MeshModel
from .meshy_utils import call_meshy_api

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
            MeshModel.objects.create(user=request.user, job_id=job_id, status="processing")
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

    # DB에 저장 (없을 경우만)
    if thumbnail_url and not mesh.image_url:
        mesh.image_url = thumbnail_url
    if video_url and not mesh.video_url:
        mesh.video_url = video_url
    mesh.status = "completed"
    mesh.save()

    return JsonResponse({
        "job_id": mesh.job_id,
        "status": mesh.status,
        "thumbnail_url": thumbnail_url,
        "video_url": video_url
    })