import json
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import MeshModel
from .meshy_utils import call_meshy_api  # Meshy API 유틸
from .azure_utils import upload_mesh_assets  # Azure 업로드 유틸


def preview_mesh_page(request, mesh_id):
    """
    특정 Mesh의 미리보기 HTML 페이지를 렌더링
    """
    mesh = get_object_or_404(MeshModel, job_id=mesh_id)
    response_data = call_meshy_api(f"/openapi/v2/text-to-3d/{mesh_id}")

    if response_data:
        return render(request, "workspace/preview_mesh.html", {
            "mesh_id": mesh_id,
            "thumbnail_url": response_data.get("thumbnail_url", ""),
            "video_url": response_data.get("video_url", "")
        })
    
    return render(request, "workspace/preview_mesh.html", {"error": "Mesh 정보를 가져올 수 없습니다."})


### 1. 모델 생성 페이지 렌더링
@login_required
def create_mesh_page(request):
    """Mesh 생성 페이지 렌더링"""
    return render(request, "workspace/create_mesh.html")


### 2. Mesh 생성 API
@csrf_exempt
@login_required
def create_mesh(request):
    """Meshy API에 요청하여 3D 모델 생성"""
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))
        prompt = data.get("prompt")
        art_style = data.get("art_style", "realistic")

        # 🔥 Meshy API 요청
        payload = {"mode": "preview", "prompt": prompt, "art_style": art_style}
        response_data = call_meshy_api("/openapi/v2/text-to-3d", "POST", payload)

        if response_data and "result" in response_data:
            job_id = response_data["result"]

            # 🔥 DB 저장
            MeshModel.objects.create(user=request.user, job_id=job_id, status="processing")

            return JsonResponse({"message": "Mesh 생성 완료", "job_id": job_id})

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format"}, status=400)

    return JsonResponse({"error": "Meshy API 요청 실패"}, status=500)


### 3. 특정 Mesh 정보 조회
@login_required
def get_mesh(request, mesh_id):
    """ 특정 Mesh 정보를 가져와서 DB 업데이트 """
    mesh = get_object_or_404(MeshModel, job_id=mesh_id)
    response_data = call_meshy_api(f"/openapi/v2/text-to-3d/{mesh_id}")

    if not response_data:
        return JsonResponse({"error": "Mesh 정보를 가져올 수 없습니다."}, status=400)

    # 🔥 API 응답 데이터
    thumbnail_url = response_data.get("thumbnail_url")
    video_url = response_data.get("video_url")
    
    # 🔥 DB 업데이트
    updated = False
    if thumbnail_url and not mesh.image_url:
        mesh.image_url = thumbnail_url
        updated = True
    if video_url and not mesh.video_url:
        mesh.video_url = video_url
        updated = True

    if updated:
        mesh.status = "completed"
        mesh.save()

    return JsonResponse({
        "job_id": mesh.job_id,
        "status": mesh.status,
        "thumbnail_url": thumbnail_url,
        "video_url": video_url
    })


### 4. 특정 Mesh 미리보기 API (JSON 반환)
@login_required
def preview_mesh(request, mesh_id):
    """Meshy API에서 모델 데이터를 조회하여 JSON으로 반환"""
    mesh = get_object_or_404(MeshModel, job_id=mesh_id)
    response_data = call_meshy_api(f"/openapi/v2/text-to-3d/{mesh_id}")

    if not response_data:
        return JsonResponse({"error": "Mesh 정보를 가져올 수 없습니다."}, status=400)

    return JsonResponse({
        "job_id": mesh.job_id,
        "status": response_data.get("status", "processing"),
        "thumbnail_url": response_data.get("thumbnail_url", ""),
        "video_url": response_data.get("video_url", ""),
        "fbx_url": response_data.get("fbx_url", "")
    })


### 5. Mesh 정제 API
@csrf_exempt
@login_required
def refine_mesh(request, mesh_id):
    """Meshy API를 호출하여 3D 모델 정제"""
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    mesh = get_object_or_404(MeshModel, job_id=mesh_id)

    payload = {"mode": "refine", "preview_task_id": mesh.job_id, "enable_pbr": True}
    response_data = call_meshy_api("/openapi/v2/text-to-3d", "POST", payload)

    if response_data and "result" in response_data:
        refined_job_id = response_data["result"]

        # 🔥 기존 Mesh 상태 업데이트
        mesh.status = "refined"
        mesh.job_id = refined_job_id
        mesh.save()

        return JsonResponse({"message": "Mesh 정제 완료", "job_id": refined_job_id})

    return JsonResponse({"error": "Mesh 정제 실패"}, status=400)


### 6. Mesh 파일을 Azure로 업로드
@login_required
def upload_mesh(request, mesh_id):
    """Meshy API에서 받은 파일을 Azure Storage에 업로드"""
    mesh = get_object_or_404(MeshModel, job_id=mesh_id)
    upload_mesh_assets(mesh)  # ✅ Azure에 업로드 수행
    return JsonResponse({"message": "Azure 업로드 완료", "job_id": mesh_id})