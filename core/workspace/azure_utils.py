import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))  # 현재 파일 경로 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))  # 상위 폴더 추가

import sys
import os
import json
import requests
from azure.storage.blob import BlobServiceClient
from utils.azure_key_manager import AzureKeyManager

class AzureBlobUploader:
    """Azure Blob Storage에 파일을 업로드하는 클래스"""

    def __init__(self, container_name="meshy-3d-assets"):
        """Azure Blob Storage 연결 초기화"""
        azure_keys = AzureKeyManager.get_instance()
        self.connection_string = azure_keys.connection_string
        self.container_name = container_name

        # Azure Blob Service Client 설정
        self.blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
        self.container_client = self.blob_service_client.get_container_client(self.container_name)

        # 컨테이너 존재 여부 확인 및 생성
        self._create_container()

    def _create_container(self):
        """컨테이너가 존재하지 않으면 생성"""
        try:
            self.container_client.create_container()
            print(f"Created container: {self.container_name}")
        except Exception:
            print(f"Container '{self.container_name}' already exists")

    def upload_blob(self, task_id: str, blob_path: str, url: str):
        """Azure Blob Storage에 파일 업로드"""
        full_blob_path = f"tasks/{task_id}/{blob_path}"  # 경로 설정

        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()

            blob_client = self.container_client.get_blob_client(full_blob_path)
            blob_client.upload_blob(response.content, overwrite=True)
            print(f"Uploaded: {full_blob_path}")

        except requests.exceptions.RequestException as e:
            print(f"Failed to upload {full_blob_path}: {e}")

    def upload_meshy_assets(self, meshy_response: dict):
        """Meshy API 응답 데이터를 기반으로 파일 업로드"""
        task_id = meshy_response["id"]

        # 모델 파일 업로드
        for model_format, url in meshy_response.get("model_urls", {}).items():
            self.upload_blob(task_id, f"models/model.{model_format}", url)

        # 썸네일 업로드
        self.upload_blob(task_id, "previews/preview.png", meshy_response.get("thumbnail_url", ""))

        # 비디오 업로드
        self.upload_blob(task_id, "videos/output.mp4", meshy_response.get("video_url", ""))

        # 원본 JSON 데이터 저장
        metadata_blob_client = self.container_client.get_blob_client(f"tasks/{task_id}/metadata.json")
        metadata_blob_client.upload_blob(json.dumps(meshy_response, indent=4), overwrite=True)
        print(f"Uploaded: tasks/{task_id}/metadata.json")