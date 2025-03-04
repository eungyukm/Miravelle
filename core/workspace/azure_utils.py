from azure.storage.blob import BlobServiceClient
import os
import requests
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

def download_file_from_url(file_url: str, temp_filename: str) -> str:
    try:
        response = requests.get(file_url, stream=True)
        if response.status_code != 200:
            return None
        
        with open(temp_filename, "wb") as temp_file:
            for chunk in response.iter_content(chunk_size=8192):
                temp_file.write(chunk)

        return temp_filename
    except Exception as e:
        return None

def upload_file_to_azure(file_path: str, task_id: str, file_type: str, blob_name: str) -> str:
    try:
        temp_file_path = None

        # download
        if file_path.startswith("http://") or file_path.startswith("https://"):
            temp_file_path = f"temp_{blob_name}"
            downloaded_path = download_file_from_url(file_path, temp_file_path)
            if not downloaded_path:
                return f"download error: {file_path}!"
            file_path = downloaded_path

        # azure save
        blob_path = f"{task_id}/{file_type}/{blob_name}"
        blob_client = blob_service_client.get_blob_client(container=AZURE_CONTAINER_NAME, blob=blob_name)

        with open(file_path, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)

            blob_url = f"https://{AZURE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net/{AZURE_CONTAINER_NAME}/{blob_path}"

            # remove temp
            if temp_file_path and os.path.exists(temp_file_path):
                os.remove(temp_file_path)

        return blob_url
    except Exception as e:
        return f"upload failed: {str(e)}!"