from azure.storage.blob import BlobServiceClient
import os

# Storage Account Name과 Key 직접 사용
AZURE_STORAGE_ACCOUNT_NAME = os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
AZURE_STORAGE_ACCOUNT_KEY = os.getenv("AZURE_STORAGE_ACCOUNT_KEY")
AZURE_CONTAINER_NAME = os.getenv("AZURE_CONTAINER_NAME")

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