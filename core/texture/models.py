from django.db import models
from django.conf import settings


"""요청을 DB에 저장하고 처리 상태를 추적하도록 설계"""
class TextureRequest(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # 유저 정보
    model_file = models.FileField(upload_to="/texture/models/")  # 3D 모델 업로드
    object_prompt = models.CharField(max_length=255)  # 오브젝트 설명
    style_prompt = models.TextField()  # 텍스처 스타일 설명
    task_id = models.CharField(max_length=100, blank=True, null=True)  # Meshy API 작업 ID
    status = models.CharField(max_length=50, default="pending")  # 요청 상태 (pending, processing, completed)
    result_url = models.URLField(blank=True, null=True)  # 결과물 URL
    created_at = models.DateTimeField(auto_now_add=True)  # 생성 시간
