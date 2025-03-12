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
            logger.info(f"MeshAsset.update_urls() 메서드는 더 이상 사용되지 않습니다. AssetListView에서 직접 URL을 업데이트합니다.")
            logger.info(f"Job ID: {job_id}의 URL 업데이트를 시도했습니다.")
            
            # 이 메서드는 더 이상 사용되지 않으므로 아무 작업도 수행하지 않습니다.
            # 실제 URL 업데이트는 AssetListView.get_context_data()에서 수행됩니다.
            
        except Exception as e:
            logger.error(f"Error in deprecated update_urls for {self.mesh_model.job_id}: {e}")
            raise