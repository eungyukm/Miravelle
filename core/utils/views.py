from django.http import JsonResponse, HttpResponseNotFound
from .azure_storage import list_blobs, file_exists, upload_file, delete_file


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