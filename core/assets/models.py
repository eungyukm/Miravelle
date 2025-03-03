from django.db import models
from django.contrib.auth.models import User

class Asset(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assets')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    file_path = models.CharField(max_length=500)  # 3D 파일 경로
    thumbnail = models.ImageField(upload_to='asset_thumbnails/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"
