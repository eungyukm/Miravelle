from django.http import HttpResponseNotFound, JsonResponse
from django.views.decorators.http import require_http_methods
from azure.storage.blob import BlobServiceClient
import uuid

# Azure Storage 관련 함수들은 주석 처리
from .azure_storage import list_blobs, file_exists, upload_file, delete_file
from .azure_key_manager import AzureKeyManager


def list_files_view(request):
    """Azure Blob Storage에 있는 파일 목록을 반환하는 API"""
    files = list_blobs()
    return JsonResponse({"files": files})


def check_file_view(request, blob_name):
    """특정 파일 존재 여부 확인 API"""
    exists = file_exists(blob_name)
    return JsonResponse({"exists": exists})


def upload_file_view(request):
    """파일 업로드 API"""
    local_file_path = "local/path/to/file.fbx"
    blob_name = "models/file.fbx"
    
    file_url = upload_file(local_file_path, blob_name)
    if file_url:
        return JsonResponse({"success": True, "file_url": file_url})
    return HttpResponseNotFound("파일 업로드 실패")


def delete_file_view(request, blob_name):
    """특정 파일 삭제 API"""
    success = delete_file(blob_name)
    if success:
        return JsonResponse({"success": True})
    return HttpResponseNotFound("파일 삭제 실패")


@require_http_methods(["GET"])
def list_files_details(request):
    """실제 메시 데이터를 반환합니다"""
    storage_account = "miravelledevstorage"
    container = "meshy-3d-assets"
    base_url = f"https://{storage_account}.blob.core.windows.net/{container}"
    
    # 실제 메시 데이터
    tasks = [
        {
            'task_id': '0195706c-4abe-7707-99cf-b719622134ed',
            'name': 'coco',  # prompt 값을 name으로 사용
            'thumbnail': "https://assets.meshy.ai/c9103216-ab25-47b6-ad99-a594f1faa190/tasks/0195706c-4abe-7707-99cf-b719622134ed/output/preview.png?Expires=4894905600&Signature=hnHkocuEopTLv~c3j5YGqWtfJVRy0rYB2oddLTHjB4rqYkToqNGzfPUmBv8Uhuh8FFZWPABCMeOfjHGmvziyGysTt7TTB2Q7ypVlUjh5wqSn2PfkSPEAMnP2QbVnTRGFbOM5lVascXFVKuj90Ae47sTFidufwdZCzxR8Qp503q5swipNds4xkWUCmREH2g~ROUnK5UqvWpxoadpF7yqBwWWpkDvOTlSI5R7T0vS2eD9wNahlFTVDWjVQxE3dc-iM9NScB6K26YBdjPT0QtJn5br7My917ARNPJdp3lGDq2UT8fcGZ1XUnmDAoSEocn00SNQBvZQuqajPovfnutm-MQ__&Key-Pair-Id=KL5I0C8H7HX83",
            'mesh_url': "https://assets.meshy.ai/c9103216-ab25-47b6-ad99-a594f1faa190/tasks/0195706c-4abe-7707-99cf-b719622134ed/output/model.fbx?Expires=4894905600&Signature=CIV5iLMimJ1iUQuijHS68D2Sgahjxm7pl4tP~ahgP7wd10smCfKuGGV45eL1WYpfIVD4W-NYyHh35GTDhg-FGHZ0wg1XXHVKRctLn7Ynd~Q49UgQfNKMZyVkHaBAWMGbOZH8aox~ZENdYIi6MobqDZAYlrfdIYe7tXgDNI0B-6PUwY3TcmZ3hM~GEq4HUyDY0neZIjk0myKc5c2eiC-dlCPdcYW0Y7A~4BQAmM-yB9VEaxOyPK7BYWInu~1uj8ONYIwkmEUZTqbmPcquNsJHmvZPuk~mGmmC-iMf0QOa3K8vDwecmzftsfScCMK2nE6r~THXBLObKWcAQ3rp0tWJEQ__&Key-Pair-Id=KL5I0C8H7HX83",
            'is_image': True,
            'created_at': 1741347900457,
            'status': 'SUCCEEDED'
        }
    ]
    
    return JsonResponse({
        "success": True,
        "message": "작업 목록을 성공적으로 가져왔습니다.",
        "tasks": tasks
    })

def get_glb_file(request, file_id):
    print(f"get_glb_file file_id {file_id}")
    """http://127.0.0.1:8000/utils/get_glb/01957d90-e660-728c-9387-84b23aa5dc6a/"""

    try:
        # UUID가 유효한지 확인
        if not isinstance(file_id, uuid.UUID):
            return JsonResponse({'error': 'Invalid UUID format'}, status=400)
        
        azure_keys = AzureKeyManager.get_instance()
        
        # Azure Blob Service 연결
        blob_service_client = BlobServiceClient.from_connection_string(azure_keys.connection_string)
        print(f"azure_keys.container_name {azure_keys.container_name}")
        container_client = blob_service_client.get_container_client(azure_keys.container_name)
        
        # Blob 경로 설정
        blob_path = f'tasks/{file_id}/models/model.glb'
        blob_client = container_client.get_blob_client(blob_path)

        if blob_client.exists():
            # HTTPS URL 반환
            blob_url = blob_client.url
            if not blob_url.startswith('https'):
                blob_url = blob_url.replace('http://', 'https://')
                
            return JsonResponse({'file_url': blob_url}, status=200)
        else:
            return JsonResponse({'error': 'File not found'}, status=404)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)