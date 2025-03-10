from django.db import models
from django.conf import settings
from django.utils import timezone
from workspace.models import MeshModel
from utils.azure_storage import upload_file, file_exists
import logging

# 로깅 설정
logger = logging.getLogger(__name__)

class Asset(models.Model): #     ┌> 사용자 모델을 참조하는 설정                           ┌> = user.assets.all()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='assets') # 사용자와 연결
    title = models.CharField(max_length=200) 
    content = models.TextField(blank=True)

    file_path = models.CharField(max_length=500)  # 3D 파일 경로
    thumbnail = models.ImageField(upload_to='asset_thumbnails/', null=True, blank=True) # 썸네일
    #                   업로드된 이미지 저장 경로 지정, <┘          └> 빈 값 허용, 업로드 안해도 됨

    # 생성일과 수정일 자동 생성
    created_at = models.DateTimeField(auto_now_add=True) # 생성일
    updated_at = models.DateTimeField(auto_now=True) # 수정일
    
    class Meta:
        ordering = ['-created_at'] # 생성일 기준 내림차순 정렬
    
    def __str__(self):
        return f"{self.title} - {self.user.username}" # 제목과 사용자 이름 반환

class MeshAsset(models.Model):
    """
    MeshModel의 에셋 정보를 저장하는 모델
    실제 데이터는 MeshModel에 있고, 이 모델은 표시용 메타데이터만 저장
    """
    mesh_model = models.OneToOneField(MeshModel, on_delete=models.CASCADE)
    
    # 에셋 표시용 메타데이터
    title = models.CharField(max_length=255, blank=True)
    prompt = models.TextField(blank=True)  # 프롬프트 저장
    thumbnail_url = models.URLField(blank=True)
    fbx_url = models.URLField(blank=True)
    
    # URL 마지막 업데이트 시간
    last_url_update = models.DateTimeField(null=True)
    
    class Meta:
        ordering = ['-mesh_model__created_at']

    def __str__(self):
        return f"Asset for {self.mesh_model.job_id}"

    def update_urls(self):
        """Azure Blob Storage URLs 업데이트"""
        try:
            job_id = self.mesh_model.job_id
            
            # 프롬프트 업데이트
            self.prompt = self.mesh_model.create_prompt
            
            # 썸네일 URL 가져오기 (previews 폴더에서 확인)
            thumbnail_path = f"tasks/{job_id}/previews/preview.png"
            logger.info(f"Checking thumbnail at path: {thumbnail_path}")
            if file_exists(thumbnail_path):
                self.thumbnail_url = f"https://miravelledevstorage.blob.core.windows.net/meshy-3d-assets/{thumbnail_path}"
                logger.info(f"Thumbnail URL updated: {self.thumbnail_url}")

            # FBX 파일 URL 가져오기 (models 폴더에서 확인)
            fbx_path = f"tasks/{job_id}/models/model.fbx"
            logger.info(f"Checking FBX at path: {fbx_path}")
            if file_exists(fbx_path):
                self.fbx_url = f"https://miravelledevstorage.blob.core.windows.net/meshy-3d-assets/{fbx_path}"
                logger.info(f"FBX URL updated: {self.fbx_url}")

            self.last_url_update = timezone.now()
            self.save()
            
        except Exception as e:
            logger.error(f"Error updating URLs for {self.mesh_model.job_id}: {e}")
            raise