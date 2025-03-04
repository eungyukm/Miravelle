from azure.storage.blob import BlobServiceClient
import os
from dotenv import load_dotenv

# 개발 환경에서만 .env 로드
load_dotenv()
    
# Storage Account Name과 Key 직접 사용
AZURE_STORAGE_ACCOUNT_NAME = os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
AZURE_STORAGE_ACCOUNT_KEY = os.getenv("AZURE_STORAGE_ACCOUNT_KEY")
AZURE_CONTAINER_NAME = os.getenv("AZURE_CONTAINER_NAME")
AZURE_CONNECTION_STRING = os.getenv("AZURE_CONNECTION_STRING")

# Blob Service Client 수동 설정
blob_service_client = BlobServiceClient(
    f"https://{AZURE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net",
    credential=AZURE_STORAGE_ACCOUNT_KEY
)

def upload_fbx_to_azure(file_path, blob_name):
    """
    AZURE_CONNECTION_STRING 없이 FBX 파일을 Azure Blob Storage에 업로드
    """
    try:
        blob_client = blob_service_client.get_blob_client(container=AZURE_CONTAINER_NAME, blob=blob_name)

        with open(file_path, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)

        return f"업로드 성공: {blob_name}"
    except Exception as e:
        return f"업로드 실패: {str(e)}"
    
def download_fbx_from_azure(blob_name, local_file_path):
    """
    Azure Blob Storage에서 FBX 파일 다운로드

    :param blob_name: Azure Blob에 저장된 파일명
    :param local_file_path: 로컬에 저장할 파일 경로
    """    
    try:
        if not AZURE_CONNECTION_STRING:
            raise ValueError("AZURE_CONNECTION_STRING is not set in environment variables")

        blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
        blob_client = blob_service_client.get_blob_client(container=AZURE_CONTAINER_NAME, blob=blob_name)

        with open(local_file_path, "wb") as file:
            file.write(blob_client.download_blob().readall())

        return f"Download successful: {local_file_path}"

    except Exception as e:
        return f"Download failed: {str(e)}"