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

def upload_file_to_azure(file_url: str, task_id: str, file_type: str, file_name: str) -> str:
    try:
        temp_file_path = None

        # download
        if file_url.startswith("http://") or file_url.startswith("https://"):
            temp_file_path = f"temp_{file_name}"
            downloaded_path = download_file_from_url(file_url, temp_file_path)
            if not downloaded_path:
                return f"download error: {file_url}!"
            file_url = downloaded_path

        # azure save
        blob_path = f"{task_id}/{file_type}/{file_name}"
        print(blob_path)
        blob_client = blob_service_client.get_blob_client(container=AZURE_CONTAINER_NAME, blob=blob_path)

        with open(file_url, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)

            blob_url = f"https://{AZURE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net/{AZURE_CONTAINER_NAME}/{blob_path}"

            # remove temp
            if temp_file_path and os.path.exists(temp_file_path):
                os.remove(temp_file_path)

        return blob_url
    except Exception as e:
        return f"upload failed: {str(e)}!"
    
# thumbnail_url = "https://assets.meshy.ai/c9103216-ab25-47b6-ad99-a594f1faa190/tasks/019560fe-4ff3-7277-8561-ddeb101d0f16/output/preview.png?Expires=4894646400&Signature=n1h7QNidmpvQfJfL2vGrY7FVrGPlO3GuhlyhCnadYggB32el~89zEQ04lql7pm13w2waMj6eyp0XKcbpPGA0ETe4Q~CC50bUJ1R2QMFR6a~vfxBdyt~3suST28I30ijU~BUU3mdZkMi2A8zfNc5YdoPrGvNBxswRT0b-yvsYfO9ydGNC7zukc6nO1ef7l~26LmDE7vni6N6cQs7laFUBArgsfSz6vk877dmDWHjbNCusPTp0ODxI6fzhgGz1PN9pZ0optZ9qLe2K9bqwf7XrRYptKmOGed6NwgDn4qfAtc5ld0OmV~S3so3Ng5l2a7OPKH-Yfm1ux27fHAy4-oiRgA__&Key-Pair-Id=KL5I0C8H7HX83"
# upload_file_to_azure(thumbnail_url, "123141", "thumbnail", "test.png")


def upload_mesh_assets(mesh):
    """
    Meshy API에서 받은 URL을 Azure로 업로드하고 MeshModel 필드 업데이트
    :param mesh: MeshModel 인스턴스
    """
    updated = False

    if mesh.image_url and not mesh.image_path:
        image_blob_url = upload_file_to_azure(mesh.image_url, mesh.job_id, "images", f"{mesh.job_id}.png")
        if "upload failed" not in image_blob_url:
            mesh.image_path = image_blob_url
            updated = True

    if mesh.video_url and not mesh.video_path:
        video_blob_url = upload_file_to_azure(mesh.video_url, mesh.job_id, "videos", f"{mesh.job_id}.mp4")
        if "upload failed" not in video_blob_url:
            mesh.video_path = video_blob_url
            updated = True

    if mesh.fbx_url and not mesh.fbx_path:
        fbx_blob_url = upload_file_to_azure(mesh.fbx_url, mesh.job_id, "fbx", f"{mesh.job_id}.fbx")
        if "upload failed" not in fbx_blob_url:
            mesh.fbx_path = fbx_blob_url
            updated = True

    if updated:
        mesh.save()
        logging.info(f"Azure 업로드 완료: {mesh.job_id}")