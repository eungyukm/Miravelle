from django.test import TestCase
from utils import upload_fbx_to_azure
from utils import download_fbx_from_azure

from dotenv import load_dotenv

# 개발 환경에서만 .env 로드
load_dotenv()

# # 로컬 테스트용 FBX 파일 경로
# local_fbx_file = "test_model.fbx"
# blob_name = "uploaded_test_model.fbx"  # Azure에 저장될 파일명

# # 업로드 테스트 실행
# result = upload_fbx_to_azure(local_fbx_file, blob_name)
# print(result)

# Azure에 업로드된 파일명
blob_name = "uploaded_test_model.fbx"
# 로컬에 저장할 경로
local_fbx_file = "downloaded_test_model.fbx"

# 다운로드 테스트 실행
result = download_fbx_from_azure(blob_name, local_fbx_file)
print(result)