from azure.storage.blob import BlobServiceClient
from .azure_key_manager import AzureKeyManager  # AzureKeyManager 클래스 가져오기

# AzureKeyManager 싱글톤 인스턴스 생성
azure_keys = AzureKeyManager.get_instance()

# Blob Service Client 설정
blob_service_client = BlobServiceClient(
    f"https://{azure_keys.storage_account_name}.blob.core.windows.net",
    credential=azure_keys.storage_account_key
)

def upload_fbx_to_azure(file_path, blob_name):
    """Azure Blob Storage에 FBX 파일 업로드"""
    try:
        blob_client = blob_service_client.get_blob_client(container=azure_keys.container_name, blob=blob_name)
        
        with open(file_path, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)
        
        return f"업로드 성공: {blob_name}"
    except Exception as e:
        return f"업로드 실패: {str(e)}"

def download_fbx_from_azure(blob_name, local_file_path):
    """Azure Blob Storage에서 FBX 파일 다운로드"""
    try:
        blob_client = blob_service_client.get_blob_client(container=azure_keys.container_name, blob=blob_name)
        
        with open(local_file_path, "wb") as file:
            file.write(blob_client.download_blob().readall())
        
        return f"Download successful: {local_file_path}"
    except Exception as e:
        return f"Download failed: {str(e)}"

def list_blobs():
    """Azure Blob Storage에서 컨테이너 내 모든 파일 목록 조회"""
    try:
        container_client = blob_service_client.get_container_client(azure_keys.container_name)
        blobs = [blob.name for blob in container_client.list_blobs()]

        print("Azure Blob Storage에 있는 파일 목록:")
        for blob in blobs:
            print(blob)
        
        return blobs
    except Exception as e:
        print(f"Azure Blob 목록 조회 실패: {str(e)}")
        return []

def file_exists(blob_name):
    """Azure Blob Storage에서 특정 파일 존재 여부 확인"""
    return blob_name in list_blobs()

def upload_file(local_path, blob_name):
    """로컬 파일을 Azure Blob Storage에 업로드"""
    try:
        blob_client = blob_service_client.get_blob_client(container=azure_keys.container_name, blob=blob_name)
        with open(local_path, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)
        
        file_url = f"https://{azure_keys.storage_account_name}.blob.core.windows.net/{azure_keys.container_name}/{blob_name}"
        print(f"{blob_name} 파일이 Azure Blob Storage에 업로드되었습니다!")
        return file_url
    except Exception as e:
        print(f"파일 업로드 실패: {str(e)}")
        return None

def delete_file(blob_name):
    """Azure Blob Storage에서 특정 파일 삭제"""
    try:
        blob_client = blob_service_client.get_blob_client(container=azure_keys.container_name, blob=blob_name)
        blob_client.delete_blob()
        print(f"{blob_name} 파일이 Azure Blob Storage에서 삭제되었습니다.")
        return True
    except Exception as e:
        print(f"파일 삭제 실패: {str(e)}")
        return False
