from django.db import models
from django.conf import settings

class TextureModel(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    job_id = models.CharField(max_length=255, unique=True)  
    name = models.CharField(max_length=255, blank=True)  
    art_style = models.CharField(max_length=50, blank=True)
    object_prompt = models.TextField(blank=True)
    style_prompt = models.TextField(blank=True)
    negative_prompt = models.TextField(blank=True)
    texture_prompt = models.TextField(blank=True)

    status = models.CharField(max_length=50, default="processing")
    progress = models.IntegerField(default=0)
    task_error = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    # URL로 파일 저장
    glb_url = models.URLField(blank=True, null=True)
    fbx_url = models.URLField(blank=True, null=True)
    obj_url = models.URLField(blank=True, null=True)
    usdz_url = models.URLField(blank=True, null=True)
    thumbnail_url = models.URLField(blank=True, null=True)

    # 텍스처 URL 저장
    base_color_url = models.URLField(blank=True, null=True)
    metallic_url = models.URLField(blank=True, null=True)
    roughness_url = models.URLField(blank=True, null=True)
    normal_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"Mesh {self.job_id} - {self.status}"
