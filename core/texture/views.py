from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.conf import settings
from .models import TextureRequest
from .texture_utils import send_texture_request, MESHY_API_URL
import requests


"""3D 모델 업로드 & API 요청 보내기"""
def upload_model(request):
    if request.method == "POST":
        model_file = request.FILES["model_file"]
        object_prompt = request.POST["object_prompt"]
        style_prompt = request.POST["style_prompt"]

        # DB에 저장
        texture_request = TextureRequest.objects.create(
            model_file=model_file,
            object_prompt=object_prompt,
            style_prompt=style_prompt
        )

        # API 요청
        model_url = request.build_absolute_uri(texture_request.model_file.url)
        response = send_texture_request(model_url, object_prompt, style_prompt)

        # task_id 저장
        texture_request.task_id = response.get("task_id")
        texture_request.status = "processing"
        texture_request.save()

        return redirect("check_status", texture_request.id)  # 상태 확인 페이지로 이동

    return render(request, "upload.html")  # HTML 폼 제공


"""작업 상태 조회"""
def check_status(request, texture_id):
    texture_request = TextureRequest.objects.get(id=texture_id)

    # Meshy API에서 상태 확인
    if texture_request.status == "processing":
        headers = {"Authorization": f"Bearer {settings.MESHY_API_KEY}"}
        response = requests.get(f"{MESHY_API_URL}/{texture_request.task_id}", headers=headers)
        response.raise_for_status()
        data = response.json()

        # 상태 업데이트
        texture_request.status = data.get("status")
        texture_request.result_url = data.get("textured_model_url", "")
        texture_request.save()

    return JsonResponse({"status": texture_request.status, "result_url": texture_request.result_url})
