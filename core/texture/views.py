from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.conf import settings
from .models import TextureModel
from .texture_utils import send_texture_request, MESHY_API_URL
import requests

from utils.azure_key_manager import AzureKeyManager

import requests
from django.http import JsonResponse, HttpResponseNotAllowed

def model_texture_form(request):
    """
    GET 요청이 들어왔을 때, 업로드 폼을 보여주는 역할만 수행
    """
    if request.method == "GET":
        return render(request, "upload.html")  # HTML 폼(예: upload.html)
    else:
        # GET 외의 요청은 허용하지 않는다면 405 에러 응답
        return HttpResponseNotAllowed(["GET"])

def model_texture_submit(request):
    """
    POST 요청(폼 전송)이 들어왔을 때, 실제로 텍스쳐 작업 API 호출 후 결과를 반환
    """
    if request.method == "POST":
        # 예: object_prompt, style_prompt 등 폼 필드를 받아 처리
        object_prompt = request.POST.get("object_prompt")
        style_prompt = request.POST.get("style_prompt")

        azure_keys = AzureKeyManager.get_instance()
        meshy_api_key = azure_keys.meshy_api_key

        payload = {
            "model_url": "https://cdn.meshy.ai/model/example_model_2.glb",
            "object_prompt": object_prompt,
            "style_prompt": style_prompt,
            "enable_original_uv": True,
            "enable_pbr": True,
            "resolution": "1024",
            "negative_prompt": "low quality, low resolution, low poly, ugly",
            "art_style": "realistic"
        }
        headers = {
            "Authorization": f"Bearer {meshy_api_key}"
        }

        try:
            response = requests.post(
                "https://api.meshy.ai/openapi/v1/text-to-texture",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            return JsonResponse(response.json(), safe=False)
        except requests.exceptions.HTTPError as e:
            return JsonResponse({"error": str(e)}, status=400)

    else:
        # POST 외의 요청은 허용하지 않는다면 405 에러 응답
        return HttpResponseNotAllowed(["POST"])

"""작업 상태 조회"""
def check_status(request, texture_id):
    texture_request = TextureModel.objects.get(id=texture_id)
    azure_keys = AzureKeyManager.get_instance()
    meshy_api_key = azure_keys.meshy_api_key  # 환경 변수에서 API 키 가져오기

    # Meshy API에서 상태 확인
    if texture_request.status == "processing":
        headers = {"Authorization": f"Bearer {meshy_api_key}"}
        response = requests.get(f"{MESHY_API_URL}/{texture_request.task_id}", headers=headers)
        response.raise_for_status()
        data = response.json()

        # 상태 업데이트
        texture_request.status = data.get("status")
        texture_request.result_url = data.get("textured_model_url", "")
        texture_request.save()

    return JsonResponse({"status": texture_request.status, "result_url": texture_request.result_url})


# 아래는 Test API 입니다.
def text_to_texture(request):
    azure_keys = AzureKeyManager.get_instance()
    meshy_api_key = azure_keys.meshy_api_key  # 환경 변수에서 API 키 가져오기

    payload = {
        "model_url": "https://cdn.meshy.ai/model/example_model_2.glb",
        "object_prompt": "a monster mask",
        "style_prompt": "red fangs, Samurai outfit that fused with japanese batik style",
        "enable_original_uv": True,
        "enable_pbr": True,
        "resolution": "1024",
        "negative_prompt": "low quality, low resolution, low poly, ugly",
        "art_style": "realistic"
    }
    headers = {
        "Authorization": f"Bearer {meshy_api_key}"
    }

    try:
        response = requests.post(
            "https://api.meshy.ai/openapi/v1/text-to-texture",
            headers=headers,
            json=payload,
        )
        response.raise_for_status()  # 오류 시 requests.exceptions.HTTPError 발생
        # response.json() 내용 확인을 위해 print
        print(response.json())
        # 최종적으로 Django view에서는 JSON 형태로 결과를 반환
        return JsonResponse(response.json(), safe=False)

    except requests.exceptions.HTTPError as e:
        # 요청이 실패했을 경우, 에러 메시지와 함께 반환
        return JsonResponse({"error": str(e)}, status=400)
    
def check_texture_status(request):
    azure_keys = AzureKeyManager.get_instance()
    meshy_api_key = azure_keys.meshy_api_key
    
    # 테스팅할 때 아래 변경해야 할 수 도 있음
    task_id = "019588fb-d84d-7cc8-a6de-3f8019b73afe"
    headers = {
        "Authorization": f"Bearer {meshy_api_key}"
    }

    try:
        response = requests.get(
            f"https://api.meshy.ai/openapi/v1/text-to-texture/{task_id}",
            headers=headers,
        )
        response.raise_for_status()  # 4xx, 5xx 에러시 예외 발생
        return JsonResponse(response.json())
    except requests.exceptions.RequestException as e:
        # 요청이 실패한 경우 에러 메시지를 반환
        return JsonResponse({"error": str(e)}, status=400)
