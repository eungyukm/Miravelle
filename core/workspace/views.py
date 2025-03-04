import json
import requests
import os
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from dotenv import load_dotenv
from .models import MeshModel

# 🔥 .env에서 API 키 로드
load_dotenv()
MESHY_API_KEY = os.getenv("MESHY_API_KEY")


# ✅ 1️⃣ 모델 생성 페이지 렌더링
@login_required
def create_mesh_page(request):
    return render(request, "workspace/create_mesh.html")


# ✅ 2️⃣ Mesh 생성 API 호출
@csrf_exempt
@login_required
def create_mesh(request):
    if request.method == "POST":
        try:
            # 🔥 요청 데이터 파싱
            data = json.loads(request.body.decode("utf-8"))
            prompt = data.get("prompt")
            art_style = data.get("art_style", "realistic")  # 기본값 설정

            print(f"🔥 [DEBUG] 요청 받음: prompt={prompt}, art_style={art_style}")

            # 🔥 Meshy API 요청 데이터 구성
            api_url = "https://api.meshy.ai/openapi/v2/text-to-3d"
            headers = {"Authorization": f"Bearer {MESHY_API_KEY}"}
            payload = {"mode": "preview", "prompt": prompt, "art_style": art_style}

            print(f"🔥 [DEBUG] API 요청 보냄: {payload}")

            # 🔥 API 요청 보내기
            response = requests.post(api_url, headers=headers, json=payload)
            response_data = response.json()

            # 🔥 API 응답 처리
            if response.status_code == 202 and "result" in response_data:
                job_id = response_data["result"]
                print(f"✅ [DEBUG] Mesh 생성 성공! 작업 ID: {job_id}")

                # 🔥 DB에 저장
                mesh = MeshModel.objects.create(user=request.user, job_id=job_id, status="processing")

                return JsonResponse({"message": "Mesh 생성 완료", "job_id": job_id})
            else:
                print(f"❌ [DEBUG] API 요청 실패: {response.status_code}, {response_data}")
                return JsonResponse({"error": "Meshy API 호출 실패"}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({"error": "잘못된 JSON 데이터"}, status=400)

    return JsonResponse({"error": "허용되지 않은 요청 방식"}, status=405)


# ✅ 3️⃣ 특정 Mesh 정보 조회 (썸네일 URL 포함)
@login_required
def get_mesh(request, mesh_id):
    """Mesh 정보를 API에서 가져와서 DB 업데이트"""
    mesh = get_object_or_404(MeshModel, job_id=mesh_id)

    api_url = f"https://api.meshy.ai/openapi/v2/text-to-3d/{mesh_id}"
    headers = {"Authorization": f"Bearer {MESHY_API_KEY}"}
    response = requests.get(api_url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        thumbnail_url = data.get("thumbnail_url", None)

        if thumbnail_url:
            mesh.preview_url = thumbnail_url  # 🔥 DB에 저장
            mesh.status = "completed"
            mesh.save()

        return JsonResponse({
            "job_id": mesh.job_id,
            "status": mesh.status,
            "preview_url": thumbnail_url if thumbnail_url else None,
            "message": "Model is still processing..." if not thumbnail_url else "Model completed"
        })

    return JsonResponse({"error": "Mesh 정보를 가져올 수 없습니다."}, status=response.status_code)


@login_required
def preview_mesh(request, mesh_id):
    """Meshy API에서 모델 데이터를 조회하여 HTML을 렌더링"""
    api_url = f"https://api.meshy.ai/openapi/v2/text-to-3d/{mesh_id}"
    headers = {"Authorization": f"Bearer {MESHY_API_KEY}"}

    response = requests.get(api_url, headers=headers)
    print(f"🔥 [DEBUG] Meshy API 응답 상태 코드: {response.status_code}")
    print(f"🔥 [DEBUG] Meshy API 응답 RAW TEXT: {response.text}")

    try:
        data = response.json()
    except json.JSONDecodeError:
        return render(request, "workspace/preview_mesh.html", {
            "mesh_id": mesh_id,
            "error_message": "⚠️ 미리보기 데이터를 불러올 수 없습니다. (Invalid JSON)"
        })

    return render(request, "workspace/preview_mesh.html", {
        "mesh_id": mesh_id,
        "thumbnail_url": data.get("thumbnail_url", ""),
        "video_url": data.get("video_url", "")
    })



# ✅ 5️⃣ HTML 렌더링: 모델 미리보기 페이지
@login_required
def preview_mesh_page(request, job_id):
    """Mesh 미리보기 페이지 렌더링"""
    print(f"🔥 [DEBUG] preview_mesh_page 호출됨: job_id={job_id}")
    return render(request, "workspace/preview_mesh.html", {"mesh_id": job_id})


# ✅ 6️⃣ Mesh 정제 API 호출
@csrf_exempt
@login_required
def refine_mesh(request, mesh_id):
    """Mesh 정제 API 호출"""
    if request.method == "POST":
        mesh = get_object_or_404(MeshModel, job_id=mesh_id)

        api_url = "https://api.meshy.ai/openapi/v2/text-to-3d"
        headers = {"Authorization": f"Bearer {MESHY_API_KEY}"}
        payload = {
            "mode": "refine",
            "preview_task_id": mesh.job_id,
            "enable_pbr": True
        }

        response = requests.post(api_url, headers=headers, json=payload)
        response_data = response.json()

        if response.status_code == 202 and "result" in response_data:
            refined_job_id = response_data["result"]
            print(f"✅ [DEBUG] 정제 성공! 새로운 작업 ID: {refined_job_id}")

            # 🔥 기존 Mesh 상태 업데이트
            mesh.status = "refined"
            mesh.job_id = refined_job_id
            mesh.save()

            return JsonResponse({"message": "Mesh 정제 완료", "job_id": refined_job_id})
        else:
            print(f"❌ [DEBUG] 정제 실패: {response.status_code}, {response_data}")
            return JsonResponse({"error": "Mesh 정제 실패"}, status=400)

    return JsonResponse({"error": "허용되지 않은 요청 방식"}, status=405)