from azure.storage.blob import BlobServiceClient
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

# Key Vault 설정
key_vault_name = "miravelle-key"
key_vault_uri = f"https://{key_vault_name}.vault.azure.net/"

# 인증 설정
credential = DefaultAzureCredential()
client = SecretClient(vault_url=key_vault_uri, credential=credential)

storage_account_name = "azure-storage-account-name"
storage_account_value = client.get_secret(storage_account_name).value

storage_account_key = "azure-storage-account-key"
storage_account_key_value = client.get_secret(storage_account_key).value

container_name = "azure-container-name"
container_name_value = client.get_secret(container_name).value

connection_string = "azure-connection-string"
connection_string_value = client.get_secret(connection_string).value

meshy_api_key = "mehsy-api-key"
meshy_api_key_value = client.get_secret(meshy_api_key).value


# Blob Service Client 수동 설정
blob_service_client = BlobServiceClient(
    f"https://{storage_account_value}.blob.core.windows.net",
    credential=storage_account_key_value
)

def upload_fbx_to_azure(file_path, blob_name):
    """
    AZURE_CONNECTION_STRING 없이 FBX 파일을 Azure Blob Storage에 업로드
    """
    try:
        blob_client = blob_service_client.get_blob_client(container=storage_account_value, blob=blob_name)

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
        if not connection_string_value:
            raise ValueError("AZURE_CONNECTION_STRING is not set in environment variables")

        blob_service_client = BlobServiceClient.from_connection_string(connection_string_value)
        blob_client = blob_service_client.get_blob_client(container=storage_account_value, blob=blob_name)

        with open(local_file_path, "wb") as file:
            file.write(blob_client.download_blob().readall())

        return f"Download successful: {local_file_path}"

    except Exception as e:
        return f"Download failed: {str(e)}"