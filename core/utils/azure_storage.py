from azure.storage.blob import BlobServiceClient
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
import os
from django.conf import settings

class AzureStorageClient:
    def __init__(self):
        """Azure Storage 클라이언트 초기화"""
        # 개발 환경(로컬 서버)에서는 환경 변수 사용 ====================
        if settings.DEBUG:
            self.storage_account = os.getenv('AZURE_STORAGE_ACCOUNT_NAME')
            self.storage_key = os.getenv('AZURE_STORAGE_ACCOUNT_KEY')
            self.container_name = os.getenv('AZURE_CONTAINER_NAME')
            self.connection_string = os.getenv('AZURE_CONNECTION_STRING')
        # ==================== 개발 환경 분기점 끝 ====================
        else:
            # Key Vault 설정 (배포 서버 프로덕션 환경)
            key_vault_name = "miravelle-key"
            key_vault_uri = f"https://{key_vault_name}.vault.azure.net/"
            credential = DefaultAzureCredential()
            client = SecretClient(vault_url=key_vault_uri, credential=credential)
            
            self.storage_account = client.get_secret("azure-storage-account-name").value
            self.storage_key = client.get_secret("azure-storage-account-key").value
            self.container_name = client.get_secret("azure-container-name").value
            self.connection_string = client.get_secret("azure-connection-string").value
        
        self.blob_service_client = BlobServiceClient(
            f"https://{self.storage_account}.blob.core.windows.net",
            credential=self.storage_key
        )
        self.container_client = self.blob_service_client.get_container_client(self.container_name)

    def list_files(self):
        """컨테이너 내 모든 파일 목록 조회"""
        try:
            return [blob.name for blob in self.container_client.list_blobs()]
        except Exception as e:
            print(f"파일 목록 조회 실패: {str(e)}")
            return []

    def upload_file(self, local_path, blob_name):
        """파일 업로드"""
        try:
            blob_client = self.container_client.get_blob_client(blob_name)
            with open(local_path, "rb") as data:
                blob_client.upload_blob(data, overwrite=True)
            return f"https://{self.storage_account}.blob.core.windows.net/{self.container_name}/{blob_name}"
        except Exception as e:
            print(f"파일 업로드 실패: {str(e)}")
            return None

    def download_file(self, blob_name, local_path):
        """파일 다운로드"""
        try:
            blob_client = self.container_client.get_blob_client(blob_name)
            with open(local_path, "wb") as file:
                file.write(blob_client.download_blob().readall())
            return True
        except Exception as e:
            print(f"파일 다운로드 실패: {str(e)}")
            return False

    def delete_file(self, blob_name):
        """파일 삭제"""
        try:
            blob_client = self.container_client.get_blob_client(blob_name)
            blob_client.delete_blob()
            return True
        except Exception as e:
            print(f"파일 삭제 실패: {str(e)}")
            return False

    def file_exists(self, blob_name):
        """파일 존재 여부 확인"""
        try:
            blob_client = self.container_client.get_blob_client(blob_name)
            return blob_client.exists()
        except Exception as e:
            print(f"파일 존재 여부 확인 실패: {str(e)}")
            return False

    def list_containers(self):
        """모든 컨테이너 목록 조회"""
        try:
            return list(self.blob_service_client.list_containers())
        except Exception as e:
            print(f"컨테이너 목록 조회 실패: {str(e)}")
            return []

    def list_blobs(self, container_name):
        """특정 컨테이너의 모든 blob 목록 조회"""
        try:
            container_client = self.blob_service_client.get_container_client(container_name)
            return list(container_client.list_blobs())
        except Exception as e:
            print(f"Blob 목록 조회 실패: {str(e)}")
            return []

    def get_blob_url(self, container_name, blob_name):
        """Blob의 URL 생성"""
        try:
            return f"https://{self.storage_account}.blob.core.windows.net/{container_name}/{blob_name}"
        except Exception as e:
            print(f"Blob URL 생성 실패: {str(e)}")
            return None

    def download_blob(self, container_name, blob_name):
        """Blob 다운로드"""
        try:
            blob_client = self.blob_service_client.get_container_client(container_name).get_blob_client(blob_name)
            return blob_client.download_blob()
        except Exception as e:
            print(f"Blob 다운로드 실패: {str(e)}")
            raise

    def upload_fbx(self, file_path, blob_name):
        """FBX 파일 업로드"""
        try:
            blob_client = self.container_client.get_blob_client(blob_name)
            with open(file_path, "rb") as data:
                blob_client.upload_blob(data, overwrite=True)
            return f"업로드 성공: {blob_name}"
        except Exception as e:
            return f"업로드 실패: {str(e)}"

    def get_files_details(self):
        """모든 컨테이너와 파일의 상세 정보를 가져오는 메서드
        
        Returns:
            list: 각 파일의 상세 정보를 담은 딕셔너리 리스트
            - name: 파일 이름
            - container: 컨테이너 이름
            - size: 파일 크기
            - content_type: 파일 타입
            - url: 파일 접근 URL
            - is_image: 이미지 파일 여부
        """
        try:
            files = []
            containers = self.list_containers()
            
            for container in containers:
                blobs = self.list_blobs(container.name)
                for blob in blobs:
                    file_info = {
                        'name': blob.name,
                        'container': container.name,
                        'size': blob.size,
                        'content_type': blob.content_settings.content_type,
                        'url': self.get_blob_url(container.name, blob.name),
                        'is_image': blob.content_settings.content_type.startswith('image/') if blob.content_settings.content_type else False
                    }
                    files.append(file_info)
            
            return files
        except Exception as e:
            print(f"파일 상세 정보 조회 실패: {str(e)}")
            return []

    def download_fbx(self, blob_name, local_file_path):
        """FBX 파일 다운로드"""
        try:
            if not self.connection_string:
                raise ValueError("connection_string이 설정되지 않았습니다.")

            blob_client = self.container_client.get_blob_client(blob_name)
            with open(local_file_path, "wb") as file:
                file.write(blob_client.download_blob().readall())
            return f"다운로드 성공: {local_file_path}"
        except Exception as e:
            return f"다운로드 실패: {str(e)}"