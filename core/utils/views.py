from django.http import JsonResponse, HttpResponseNotFound, FileResponse
from django.views.decorators.http import require_http_methods
from .azure_storage import AzureStorageClient


def list_files_view(request):
    """Azure Blob Storage에 있는 파일 목록을 반환하는 API"""
    azure_client = AzureStorageClient()
    files = azure_client.list_files()
    return JsonResponse({"files": files})


def check_file_view(request, blob_name):
    """특정 파일 존재 여부 확인 API"""
    azure_client = AzureStorageClient()
    exists = azure_client.file_exists(blob_name)
    return JsonResponse({"exists": exists})


def upload_file_view(request):
    """파일 업로드 API"""
    local_file_path = "local/path/to/file.fbx" # 로컬 파일 경로
    blob_name = "models/file.fbx" # 업로드할 파일 경로
    
    azure_client = AzureStorageClient() # Azure Storage 클라이언트 초기화
    file_url = azure_client.upload_file(local_file_path, blob_name) # 파일 업로드
    if file_url:
        return JsonResponse({"success": True, "file_url": file_url}) # 성공시 파일 URL 반환
    return HttpResponseNotFound("파일 업로드 실패") # 실패시 404 오류 반환


def delete_file_view(request, blob_name):
    """특정 파일 삭제 API"""
    azure_client = AzureStorageClient()
    success = azure_client.delete_file(blob_name)
    if success:
        return JsonResponse({"success": True})
    return HttpResponseNotFound("파일 삭제 실패")

# 추가 코드
@require_http_methods(["GET"])
def list_files_details(request):
    """Azure Blob Storage의 모든 컨테이너와 파일의 상세 정보를 가져오는 API
    
    Returns:
        JsonResponse: 파일 상세 정보 목록 또는 에러 메시지
        - 성공시: {"success": True, "message": "성공 메시지", "files": [파일 상세 정보 목록]}
        - 실패시: {"success": False, "message": "에러 메시지", "files": []}, status=500
    """
    try:
        # Azure Storage 클라이언트 초기화
        azure_client = AzureStorageClient()
        
        # 모든 파일의 상세 정보 가져오기
        files = azure_client.get_files_details()
        
        if not files:
            return JsonResponse({
                "success": True,
                "message": "파일이 없거나 접근할 수 없습니다.",
                "files": []
            })
            
        return JsonResponse({
            "success": True,
            "message": "파일 목록을 성공적으로 가져왔습니다.",
            "files": files
        })
        
    except Exception as e:
        return JsonResponse({
            "success": False,
            "message": f"파일 목록 조회 중 오류 발생: {str(e)}",
            "files": []
        }, status=500)


@require_http_methods(["GET"])
def download_file(request, file_path):
    """Azure Blob Storage에서 파일을 다운로드하는 API
    
    Args:
        request: HTTP 요청 객체
        file_path (str): 'container/blob_name' 형식의 파일 경로
    
    Returns:
        FileResponse: 파일 다운로드 응답
        JsonResponse: 에러 발생시 에러 메시지 반환
    
    파일 경로는 반드시 'container/blob_name' 형식이어야 함
    예: 'images/sample.jpg', 'models/character.fbx'
    """
    try:
        # Azure Storage 클라이언트 초기화
        azure_client = AzureStorageClient()
        
        # 파일 경로에서 컨테이너와 blob 이름 추출
        container_name, blob_name = file_path.split('/', 1)
        
        # 파일 다운로드
        blob_data = azure_client.download_blob(container_name, blob_name)
        
        # FileResponse로 반환
        response = FileResponse(blob_data)
        response['Content-Disposition'] = f'attachment; filename="{blob_name}"'
        return response
    
    except ValueError:
        return JsonResponse({'error': '잘못된 파일 경로 형식입니다. "container/blob_name" 형식이어야 합니다.'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)