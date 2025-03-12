from django.shortcuts import render, redirect
from django.http import StreamingHttpResponse, JsonResponse, HttpResponseNotAllowed, Http404
from .models import TextureModel
from workspace.models import MeshModel
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from utils.azure_key_manager import AzureKeyManager

import requests
import json
from urllib.parse import unquote

def model_texture_form(request):
    """
    GET 요청이 들어왔을 때, 업로드 폼을 보여주는 역할만 수행
    """
    if request.method == "GET":
        # 업로드 작업 ID
        source_model_id = request.GET.get("task_id")
        print(f"source_model_id {source_model_id}")

        return render(request, "upload.html", {"source_model_id": source_model_id})
    else:
        # GET 외의 요청은 허용하지 않는다면 405 에러 응답
        return HttpResponseNotAllowed(["GET"])

# @csrf_protect
def model_texture_submit(request):
    if request.method == "POST":
        object_prompt = request.POST.get("object_prompt")
        style_prompt = request.POST.get("style_prompt")
        source_model_id = request.POST.get("source_model_id")

        # 값이 None이거나 비어있으면 오류 반환
        if not source_model_id:
            print("Missing source_model_id")
            return JsonResponse({"error": "Missing source_model_id"}, status=400)

        # 모델 객체 검색 (존재하지 않을 경우 404 처리)
        try:
            mesh = get_object_or_404(MeshModel, job_id=source_model_id)
            print(f"Found MeshModel: {mesh.job_id}")
            print(f"glb_path (raw): {mesh.glb_path}")
        except Http404:
            print(f"MeshModel with job_id {source_model_id} not found!")
            return JsonResponse({"error": "MeshModel not found."}, status=404)

        # URL 디코딩
        model_url = unquote(str(mesh.glb_path.url)) if mesh.glb_path else None
        print(f"Decoded Model URL: {model_url}")

        # URL 수정 단계
        if model_url:
            # '/media/' 자동 추가 부분 제거
            model_url = model_url.replace("/media/", "")

            # 'https:/ ' → 'https://'로 변환
            if model_url.startswith("https:/") and not model_url.startswith("https://"):
                model_url = model_url.replace("https:/", "https://")

            # 'https://media/' 잘못된 부분 제거
            if model_url.startswith("https://media/"):
                model_url = model_url.replace("https://media/", "https://")

        # URL 값이 없으면 오류 반환
        if not model_url:
            print("Model URL not found")
            return JsonResponse({"error": "Model URL is missing."}, status=400)

        print(f"Final Model URL: {model_url}")

        # Meshy API 호출 설정
        azure_keys = AzureKeyManager.get_instance()
        meshy_api_key = azure_keys.meshy_api_key

        payload = {
            "model_url": model_url,
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
            # Meshy API 호출
            response = requests.post(
                "https://api.meshy.ai/openapi/v1/text-to-texture",
                headers=headers,
                json=payload
            )
            response.raise_for_status()

            result = response.json()
            texture_task_id = result.get("result")

            if not texture_task_id:
                print("Failed to create texture task.")
                return JsonResponse({"error": "Failed to create texture task."}, status=400)

            return JsonResponse({
                "texture_task_id": texture_task_id,
                "status": "processing"
            })

        except requests.exceptions.RequestException as e:
            print(f"Meshy API Error: {e}")
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid request"}, status=400)

def check_status(request, task_id):
    azure_keys = AzureKeyManager.get_instance()
    meshy_api_key = azure_keys.meshy_api_key

    url = f"https://api.meshy.ai/openapi/v1/text-to-texture/{task_id}/status"
    headers = {
        "Authorization": f"Bearer {meshy_api_key}"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        # 상태 및 진행률 반환
        return JsonResponse(data)
    except requests.exceptions.RequestException as e:
        return JsonResponse({"error": str(e)}, status=400)



def texture_status_stream(request, task_id):
    azure_keys = AzureKeyManager.get_instance()
    meshy_api_key = azure_keys.meshy_api_key

    def event_stream():
        url = f"https://api.meshy.ai/openapi/v1/text-to-texture/{task_id}/stream"
        headers = {
            "Authorization": f"Bearer {meshy_api_key}"
        }

        try:
            response = requests.get(url, headers=headers, stream=True)
            response.raise_for_status()

            for line in response.iter_lines():
                if line:
                    if line.startswith(b"data:"):
                        data = json.loads(line.decode("utf-8")[5:])
                        print("Received Data:", data)

                        # 진행률 및 상태 반환
                        progress = data.get('progress', 0)
                        status = data.get('status')

                        # 완료 시 이미지 및 비디오 URL 추가
                        thumbnail_url = data.get('thumbnail_url')
                        
                        yield f"data: {json.dumps({'progress': progress, 'status': status, 'thumbnail_url': thumbnail_url})}\n\n"

                        # 상태 완료 시 종료
                        if status in ["SUCCEEDED", "FAILED", "CANCELED"]:
                            break

        except requests.exceptions.RequestException as e:
            yield f"data: {{\"error\": \"{str(e)}\"}}\n\n"

    return StreamingHttpResponse(event_stream(), content_type="text/event-stream")



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