from django.db import models
from django.conf import settings

class MeshModel(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    job_id = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=50, default="processing")
    created_at = models.DateTimeField(auto_now_add=True)
    create_prompt = models.TextField()

    image_path = models.FileField(max_length=500, blank=True, null=True)
    video_path = models.FileField(max_length=500, blank=True, null=True)
    fbx_path = models.FileField(max_length=500, blank=True, null=True)
    glb_path = models.FileField(max_length=500, blank=True, null=True)
    obj_path = models.FileField(max_length=500, blank=True, null=True)
    usdz_path = models.FileField(max_length=500, blank=True, null=True)
    metadata_path = models.FileField(max_length=500, blank=True, null=True)
    base_color_path = models.FileField(max_length=500, blank=True, null=True)

    def __str__(self):
        return f"Mesh {self.job_id} - {self.status}"
