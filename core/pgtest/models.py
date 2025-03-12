from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class TestMeshModel(models.Model):
    """PostgreSQL 테스트용 메시 모델"""
    job_id = models.CharField(max_length=100, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='test_mesh_models')
    create_prompt = models.TextField(blank=True, null=True)
    image_path = models.CharField(max_length=255, blank=True, null=True)
    fbx_path = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = '테스트 메시 모델'
        verbose_name_plural = '테스트 메시 모델 목록'
    
    def __str__(self):
        return f"TestMesh: {self.job_id[:8]}"

class TestMeshAsset(models.Model):
    """PostgreSQL 테스트용 메시 에셋"""
    mesh_model = models.OneToOneField(TestMeshModel, on_delete=models.CASCADE, related_name='test_asset')
    title = models.CharField(max_length=100)
    prompt = models.TextField(blank=True, null=True)
    thumbnail_url = models.URLField(blank=True, null=True)
    fbx_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = '테스트 메시 에셋'
        verbose_name_plural = '테스트 메시 에셋 목록'
    
    def __str__(self):
        return self.title