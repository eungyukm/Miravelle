import os
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv
import mimetypes

# MIME 타입 초기화
mimetypes.init()

# .env 파일 로드
load_dotenv()

def upload_all_static_files_to_azure(directory):
    """지정된 디렉토리의 모든 파일을 Azure Blob Storage에 MIME 타입과 함께 업로드"""

    # 환경 변수에서 값 읽기
    AZURE_STORAGE_ACCOUNT_NAME = os.getenv('AZURE_STORAGE_ACCOUNT_NAME')
    AZURE_STORAGE_ACCOUNT_KEY = os.getenv('AZURE_STORAGE_ACCOUNT_KEY')
    AZURE_STATIC_CONTAINER_NAME = os.getenv('AZURE_STATIC_CONTAINER_NAME')
    AZURE_CONNECTION_STRING = os.getenv('AZURE_CONNECTION_STRING')

    # 환경 변수 확인
    if not all([AZURE_STORAGE_ACCOUNT_NAME, AZURE_STORAGE_ACCOUNT_KEY, AZURE_STATIC_CONTAINER_NAME, AZURE_CONNECTION_STRING]):
        print("환경 변수가 올바르게 설정되지 않았습니다.")
        return

    # BlobServiceClient 설정
    try:
        blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
    except Exception as e:
        print(f"BlobServiceClient 생성 실패: {e}")
        return

    success_count = 0
    fail_count = 0

    if not os.path.isdir(directory):
        print(f"디렉토리가 존재하지 않습니다: {directory}")
        return
    
    file_list = []
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            # 업로드할 blob 경로 설정 (디렉토리 구조 유지)
            blob_name = os.path.relpath(file_path, directory).replace("\\", "/")
            file_list.append((file_path, blob_name))

    total_files = len(file_list)
    print(f"\n=== 업로드 시작 (총 {total_files}개 파일) ===\n")

    for i, (file_path, blob_name) in enumerate(file_list, 1):
        try:
            # MIME 타입 추측
            mime_type, _ = mimetypes.guess_type(file_path)
            if mime_type is None:
                mime_type = "application/octet-stream"  # 기본값

            # Blob 클라이언트 생성
            blob_client = blob_service_client.get_blob_client(container=AZURE_STATIC_CONTAINER_NAME, blob=blob_name)
            
            # 파일 열기 및 업로드 (MIME 타입 지정)
            with open(file_path, "rb") as data:
                blob_client.upload_blob(data, overwrite=True, content_type=mime_type)

            print(f"[{i}/{total_files}] 업로드 성공: {blob_name} (MIME: {mime_type})")
            success_count += 1
        except Exception as e:
            print(f"[{i}/{total_files}] 업로드 실패: {blob_name} - 오류: {str(e)}")
            fail_count += 1

    # 업로드 결과 출력
    print("\n=== 업로드 결과 ===")
    print(f"성공한 파일 수: {success_count}")
    print(f"실패한 파일 수: {fail_count}")

def delete_all_files_in_container():
    """Azure Blob Storage에서 컨테이너 내 모든 파일 삭제"""
    
    # 환경 변수에서 값 읽기
    AZURE_CONTAINER_NAME = os.getenv('AZURE_STATIC_CONTAINER_NAME')
    AZURE_CONNECTION_STRING = os.getenv('AZURE_CONNECTION_STRING')

    if not AZURE_CONTAINER_NAME or not AZURE_CONNECTION_STRING:
        print("환경 변수가 올바르게 설정되지 않았습니다.")
        return

    try:
        blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
        container_client = blob_service_client.get_container_client(AZURE_CONTAINER_NAME)
        blobs = container_client.list_blobs()

        total_files = 0
        deleted_files = 0
        failed_files = 0

        print(f"\n=== {AZURE_CONTAINER_NAME} 컨테이너의 파일 삭제 시작 ===")

        for blob in blobs:
            total_files += 1
            try:
                blob_client = container_client.get_blob_client(blob.name)
                blob_client.delete_blob()
                deleted_files += 1
                print(f"삭제 성공: {blob.name}")
            except Exception as e:
                failed_files += 1
                print(f"삭제 실패: {blob.name} - 오류: {str(e)}")

        # 삭제 결과 출력
        print("\n=== 삭제 결과 ===")
        print(f"총 파일 수: {total_files}")
        print(f"삭제된 파일 수: {deleted_files}")
        print(f"삭제 실패 파일 수: {failed_files}")

    except Exception as e:
        print(f"컨테이너 파일 삭제 실패: {e}")

# 실행 코드
if __name__ == "__main__":
    static_dir = "core/staticfiles/"  # 업로드할 로컬 디렉토리
    
    # 삭제 후 업로드 실행
    delete_all_files_in_container()
    upload_all_static_files_to_azure(static_dir)