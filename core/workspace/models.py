from django.conf import settings
from django.db import models

class MeshModel(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # 🔥 수정
    job_id = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=50, default="processing")
    created_at = models.DateTimeField(auto_now_add=True)
