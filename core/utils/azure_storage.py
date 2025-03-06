# from azure.storage.blob import BlobServiceClient
# from azure.identity import DefaultAzureCredential
# from azure.keyvault.secrets import SecretClient

# # Key Vault 설정
# key_vault_name = "miravelle-key"
# key_vault_uri = f"https://{key_vault_name}.vault.azure.net/"

# # 인증 설정
# credential = DefaultAzureCredential()
# client = SecretClient(vault_url=key_vault_uri, credential=credential)

# storage_account_name = "azure-storage-account-name"
# storage_account_value = client.get_secret(storage_account_name).value

# storage_account_key = "azure-storage-account-key"
# storage_account_key_value = client.get_secret(storage_account_key).value

# container_name = "azure-container-name"
# container_name_value = client.get_secret(container_name).value

# connection_string = "azure-connection-string"
# connection_string_value = client.get_secret(connection_string).value

# meshy_api_key = "mehsy-api-key"
# meshy_api_key_value = client.get_secret(meshy_api_key).value

# # Blob Service Client 설정
# blob_service_client = BlobServiceClient(
#     f"https://{storage_account_value}.blob.core.windows.net",
#     credential=storage_account_key_value
# )


# def upload_fbx_to_azure(file_path, blob_name):
#     """Azure Blob Storage에 FBX 파일 업로드"""
#     try:
#         blob_client = blob_service_client.get_blob_client(container=connection_string_value, blob=blob_name)

#         with open(file_path, "rb") as data:
#             blob_client.upload_blob(data, overwrite=True)

#         return f"업로드 성공: {blob_name}"
#     except Exception as e:
#         return f"업로드 실패: {str(e)}"


# def download_fbx_from_azure(blob_name, local_file_path):
#     """Azure Blob Storage에서 FBX 파일 다운로드"""
#     try:
#         if not connection_string_value:
#             raise ValueError("AZURE_CONNECTION_STRING is not set in environment variables")

#         blob_service_client = BlobServiceClient.from_connection_string(connection_string_value)
#         blob_client = blob_service_client.get_blob_client(container=container_name_value, blob=blob_name)

#         with open(local_file_path, "wb") as file:
#             file.write(blob_client.download_blob().readall())

#         return f"Download successful: {local_file_path}"

#     except Exception as e:
#         return f"Download failed: {str(e)}"


# def list_blobs():
#     """Azure Blob Storage에서 컨테이너 내 모든 파일 목록 조회"""
#     try:
#         container_client = blob_service_client.get_container_client(container_name_value)
#         blobs = [blob.name for blob in container_client.list_blobs()]

#         print("Azure Blob Storage에 있는 파일 목록:")
#         for blob in blobs:
#             print(blob)

#         return blobs
#     except Exception as e:
#         print(f"Azure Blob 목록 조회 실패: {str(e)}")
#         return []


# def file_exists(blob_name):
#     """Azure Blob Storage에서 특정 파일 존재 여부 확인"""
#     return blob_name in list_blobs()


# def upload_file(local_path, blob_name):
#     """로컬 파일을 Azure Blob Storage에 업로드"""
#     try:
#         blob_client = blob_service_client.get_blob_client(container=container_name_value, blob=blob_name)
#         with open(local_path, "rb") as data:
#             blob_client.upload_blob(data, overwrite=True)

#         file_url = f"https://{storage_account_key_value}.blob.core.windows.net/{container_name_value}/{blob_name}"
#         print(f"{blob_name} 파일이 Azure Blob Storage에 업로드되었습니다!")
#         return file_url
#     except Exception as e:
#         print(f"파일 업로드 실패: {str(e)}")
#         return None


# def delete_file(blob_name):
#     """Azure Blob Storage에서 특정 파일 삭제"""
#     try:
#         blob_client = blob_service_client.get_blob_client(container=container_name_value, blob=blob_name)
#         blob_client.delete_blob()
#         print(f"{blob_name} 파일이 Azure Blob Storage에서 삭제되었습니다.")
#         return True
#     except Exception as e:
#         print(f"파일 삭제 실패: {str(e)}")
#         return False