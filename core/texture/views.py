from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.conf import settings
from .models import TextureModel
from .texture_utils import send_texture_request, MESHY_API_URL
from django.urls import reverse
from urllib.parse import urlencode

from utils.azure_key_manager import AzureKeyManager

import requests
import json
from django.http import JsonResponse, HttpResponseNotAllowed

def model_texture_form(request):
    """
    GET 요청이 들어왔을 때, 업로드 폼을 보여주는 역할만 수행
    """
    if request.method == "GET":
        # 업로드 작업 ID
        source_model_id = request.POST.get("source_model_id")
        print(f"source_model_id {source_model_id}")

        # 텍스쳐링 작업 ID
        texture_task_id = request.POST.get("texture_task_id")
        print(f"texture_task_id {texture_task_id}")

        return render(request, "upload.html", {"source_model_id": source_model_id})
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

        # 업로드 작업 ID
        source_model_id = request.POST.get("source_model_id")
        print(source_model_id)

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
            print(f"response.json {response.json()}")

            result = response.json()
            texture_task_id = result.get("result")

            url = reverse('model_texture_form')
            query_params = urlencode({
                'texture_task_id': texture_task_id
            })

            return redirect(f"{url}?{query_params}")
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


# ============================ 아래는 Test API 입니다. ============================
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


def texuring_streaming(request):
    """
    테스트용 뷰: Meshy.ai 스트리밍 API를 호출해보고
    status가 완료(SUCCEEDED/FAILED/CANCELED)될 때까지
    데이터를 받아온 뒤 마지막 상태를 반환.
    """
    azure_keys = AzureKeyManager.get_instance()
    meshy_api_key = azure_keys.meshy_api_key
    task_id = "019588fb-d84d-7cc8-a6de-3f8019b73afe"

    headers = {
        "Authorization": f"Bearer {meshy_api_key}",
        "Accept": "text/event-stream"
    }

    url = f"https://api.meshy.ai/openapi/v1/text-to-texture/{task_id}/stream"

    final_data = None
    try:
        with requests.get(url, headers=headers, stream=True) as response:
            response.raise_for_status()  # 4xx, 5xx 에러시 예외 발생

            # 스트리밍 응답을 한 줄씩 읽어옴
            for line in response.iter_lines():
                if line and line.startswith(b'data:'):
                    # 앞의 'data:'를 제외하고 JSON 디코딩
                    data_str = line.decode('utf-8')[5:]
                    data = json.loads(data_str)

                    # 콘솔에서 실시간 확인
                    print("Received Data:", data)

                    # 예: 상태가 완료되면 중단
                    if data.get('status') in ['SUCCEEDED', 'FAILED', 'CANCELED']:
                        final_data = data
                        break

        # 모두 읽고 나면, 혹은 중간에 break된 후 최종 상태를 반환
        if final_data is not None:
            return JsonResponse({"final_status": final_data['status'], "data": final_data})
        else:
            return JsonResponse({"info": "Streaming ended or no final status found."})

    except requests.exceptions.RequestException as e:
        # HTTPError, ConnectionError 등 모든 requests 예외 처리
        return JsonResponse({"error": str(e)}, status=400)