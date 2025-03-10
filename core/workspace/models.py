from django.conf import settings
from django.db import models

class MeshModel(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # 유저 정보
    job_id = models.CharField(max_length=255, unique=True)  # Meshy 작업 ID
    status = models.CharField(max_length=50, default="processing")  # 모델 상태
    created_at = models.DateTimeField(auto_now_add=True)  # 생성 날짜
    create_prompt = models.TextField()  # 생성 프롬프트 저장

    # Azure Storage에 저장된 파일 경로
    image_path = models.FileField(blank=True, null=True)
    video_path = models.FileField(blank=True, null=True)
    fbx_path = models.FileField(blank=True, null=True)
    glb_path = models.FileField(blank=True, null=True)
    obj_path = models.FileField(blank=True, null=True)
    usdz_path = models.FileField(blank=True, null=True)
    metadata_path = models.FileField(blank=True, null=True)

    def __str__(self):
        return f"Mesh {self.job_id} - {self.status}"