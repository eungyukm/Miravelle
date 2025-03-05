import json
import requests
import os
import logging
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()
MESHY_API_KEY = os.getenv("MESHY_API_KEY")

# 로깅 설정
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def call_meshy_api(endpoint: str, method: str = "GET", payload: dict = None):
    """
    Meshy API 호출을 위한 유틸 함수
    :param endpoint: API 엔드포인트 (예: "/openapi/v2/text-to-3d")
    :param method: HTTP 메서드 ("GET" 또는 "POST")
    :param payload: POST 요청 시 데이터
    :return: 응답 데이터 (dict) 또는 None
    """
    api_url = f"https://api.meshy.ai{endpoint}"
    headers = {"Authorization": f"Bearer {MESHY_API_KEY}"}

    try:
        if method == "GET":
            response = requests.get(api_url, headers=headers)
        elif method == "POST":
            response = requests.post(api_url, headers=headers, json=payload)
        else:
            logging.error(f"Unsupported HTTP method: {method}")
            return None

        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        logging.error(f"Meshy API 요청 실패: {e}")
        return None