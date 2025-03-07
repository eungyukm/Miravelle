import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))  # 현재 파일 경로 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))  # 상위 폴더 추가

import json
import requests
import logging
from utils.azure_key_manager import AzureKeyManager

# 로깅 설정
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


# meshy_utils.py 수정 (SSE 스트림 처리 추가 및 디버깅 유지)
def call_meshy_api(endpoint: str, method: str = "GET", payload: dict = None, stream: bool = False):
    """
    Meshy API 호출을 위한 유틸 함수 (디버깅 추가, SSE 스트림 처리)
    """
    api_url = f"https://api.meshy.ai{endpoint}"
    azure_keys = AzureKeyManager.get()
    headers = {"Authorization": f"Bearer {azure_keys.meshy_api_key}"}

    try:
        logging.info(f"API 요청 URL: {api_url}")
        logging.info(f"API 요청 헤더: {headers}")
        if payload:
            logging.info(f"API 요청 페이로드: {payload}")

        if method == "GET":
            response = requests.get(api_url, headers=headers, stream=stream)
        elif method == "POST":
            response = requests.post(api_url, headers=headers, json=payload, stream=stream)
        else:
            logging.error(f"Unsupported HTTP method: {method}")
            return None

        logging.info(f"Meshy API 응답 코드: {response.status_code}")

        # 스트리밍이면 response 객체 자체를 반환
        if stream:
            return response

        logging.info(f"Meshy API 응답 데이터: {response.text}")  # 응답 내용 출력
        response.raise_for_status()

        try:
            return response.json()
        except json.JSONDecodeError:
            logging.error("응답 데이터가 JSON 형식이 아닙니다.")
            return None

    except requests.exceptions.RequestException as e:
        logging.error(f"Meshy API 요청 실패: {e}")
        return None