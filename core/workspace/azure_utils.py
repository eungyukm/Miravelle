import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))  # 현재 파일 경로 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))  # 상위 폴더 추가

import json
import requests
from azure.storage.blob import BlobServiceClient
from utils.azure_key_manager import AzureKeyManager
from .models import MeshModel
from users.models import User

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

            # 업로드된 URL 반환
            return blob_client.url

        except requests.exceptions.RequestException as e:
            print(f"Failed to upload {full_blob_path}: {e}")
            return None

    def upload_meshy_assets(self, request, meshy_response: dict):
        """Meshy API 응답 데이터를 기반으로 파일 업로드 및 모델 저장"""
        task_id = meshy_response["id"]

        user_id = request.session.get('user_id')
        if not user_id:
            raise ValueError("User not authenticated")

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise ValueError("User not found")

        # get_or_create로 중복 저장 방지
        mesh_model, created = MeshModel.objects.get_or_create(
            job_id=task_id,
            defaults={
                'user': user,
                'create_prompt': meshy_response.get("prompt", ""),
                'status': 'processing'
            }
        )

        if not created:
            print(f"MeshModel with job_id={task_id} already exists, updating fields")

        # 모델 파일 업로드 후 저장
        for model_format, url in meshy_response.get("model_urls", {}).items():
            if url:
                uploaded_url = self.upload_blob(task_id, f"models/model.{model_format}", url)
                if uploaded_url:
                    if model_format == 'fbx':
                        mesh_model.fbx_path = uploaded_url
                    elif model_format == 'glb':
                        mesh_model.glb_path = uploaded_url
                    elif model_format == 'obj':
                        mesh_model.obj_path = uploaded_url
                    elif model_format == 'usdz':
                        mesh_model.usdz_path = uploaded_url

        # 썸네일 업로드
        if meshy_response.get("thumbnail_url"):
            uploaded_url = self.upload_blob(task_id, "previews/preview.png", meshy_response.get("thumbnail_url"))
            if uploaded_url:
                mesh_model.image_path = uploaded_url

        # 비디오 업로드
        if meshy_response.get("video_url"):
            uploaded_url = self.upload_blob(task_id, "videos/output.mp4", meshy_response.get("video_url"))
            if uploaded_url:
                mesh_model.video_path = uploaded_url

        # 원본 JSON 데이터 저장
        metadata_blob_client = self.container_client.get_blob_client(f"tasks/{task_id}/metadata.json")
        metadata_blob_client.upload_blob(json.dumps(meshy_response, indent=4), overwrite=True)
        metadata_url = metadata_blob_client.url
        mesh_model.metadata_path = metadata_url

        # 상태 업데이트 및 저장
        mesh_model.status = "completed"
        mesh_model.save()
        print(f"MeshModel saved: {mesh_model}")

    def upload_refine_assets(self, request, meshy_response: dict):
        """Meshy API 응답 데이터를 기반으로 Refine 파일 업로드 및 모델 저장"""
        task_id = meshy_response.get("job_id")
        if not task_id:
            raise ValueError("Meshey response does not contain 'job_id': " + str(meshy_response))

        user_id = request.session.get('user_id')
        if not user_id:
            raise ValueError("User not authenticated")

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise ValueError("User not found")

        # 프롬프트를 조건으로 사용하여 update_or_create 수행
        prompt = meshy_response.get("prompt", "")
        mesh_model, created = MeshModel.objects.update_or_create(
            create_prompt=prompt,
            defaults={
                'job_id': task_id,
                'user': user,
                'status': 'processing'
            }
        )

        if not created:
            print(f"MeshModel with prompt='{prompt}' already exists, updating fields")

        # 모델 파일 업로드 후 저장
        for model_format, url in meshy_response.get("model_urls", {}).items():
            if url:
                uploaded_url = self.upload_blob(task_id, f"models/model.{model_format}", url)
                if uploaded_url:
                    if model_format == 'fbx':
                        mesh_model.fbx_path = uploaded_url
                    elif model_format == 'glb':
                        mesh_model.glb_path = uploaded_url
                    elif model_format == 'obj':
                        mesh_model.obj_path = uploaded_url
                    elif model_format == 'usdz':
                        mesh_model.usdz_path = uploaded_url

        # 썸네일 업로드
        if meshy_response.get("thumbnail_url"):
            uploaded_url = self.upload_blob(task_id, "previews/preview.png", meshy_response.get("thumbnail_url"))
            if uploaded_url:
                mesh_model.image_path = uploaded_url

        # 비디오 업로드
        if meshy_response.get("video_url"):
            uploaded_url = self.upload_blob(task_id, "videos/output.mp4", meshy_response.get("video_url"))
            if uploaded_url:
                mesh_model.video_path = uploaded_url

        # 텍스쳐 업로드: base_color_path
        texture_urls = meshy_response.get("texture_urls", [])
        if texture_urls and isinstance(texture_urls, list):
            for texture in texture_urls:
                base_color_url = texture.get("base_color")
                if base_color_url:
                    uploaded_url = self.upload_blob(task_id, "textures/base_color.png", base_color_url)
                    if uploaded_url:
                        mesh_model.base_color_path = uploaded_url
                    break  # 첫번째 base_color만 처리

        # 원본 JSON 데이터 저장
        metadata_blob_client = self.container_client.get_blob_client(f"tasks/{task_id}/metadata.json")
        metadata_blob_client.upload_blob(json.dumps(meshy_response, indent=4), overwrite=True)
        metadata_url = metadata_blob_client.url
        mesh_model.metadata_path = metadata_url

        # 상태 업데이트 및 저장
        mesh_model.status = "refine-completed"
        mesh_model.save()
        print(f"MeshModel saved: {mesh_model}")