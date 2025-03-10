import requests  # HTTP 요청을 보내기 위한 라이브러리

"""Meshy API에 요청을 보내고, 작업 ID를 받아옴"""
import requests
from workspace.meshy_utils import call_meshy_api

MESHY_API_URL = "https://api.meshy.ai/openapi/v1/text-to-texture"
API_KEY = call_meshy_api  # utils 앱에서 AzureKeyManager가 API 데려옴

def send_texture_request(model_url, object_prompt, style_prompt):
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
    headers = {"Authorization": f"Bearer {API_KEY}"}

    response = requests.post(MESHY_API_URL, headers=headers, json=payload)
    print("response.request.url : ", response.request.url)
    response.raise_for_status()  # 오류 발생 시 예외 처리
    return response.json()  # {'task_id': '018a210d-8ba4-705c-b111-1f1776f7f578'}