from django.conf import settings
from django.db import models

class MeshModel(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    job_id = models.CharField(max_length=255, unique=True)  # Meshy 작업 ID
    status = models.CharField(max_length=50, default="processing")
    created_at = models.DateTimeField(auto_now_add=True)
    create_prompt = models.TextField()  # 생성 프롬프트 (원하는 경우)

    # Azure Storage에 저장될 파일들 (upload_to는 로컬이 아닌 "Blob 내부 경로"가 됨)
    image_path = models.FileField(blank=True, null=True)
    video_path = models.FileField(blank=True, null=True)
    fbx_path = models.FileField(blank=True, null=True)
    glb_path = models.FileField(blank=True, null=True)
    obj_path = models.FileField(blank=True, null=True)
    usdz_path = models.FileField(blank=True, null=True)
    metadata_path = models.FileField(blank=True, null=True)

    def __str__(self):
        return f"Mesh {self.job_id} - {self.status}"