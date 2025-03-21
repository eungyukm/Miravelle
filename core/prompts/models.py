from django.conf import settings
from django.db import models

class MeshPromptModel(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    job_id = models.CharField(max_length=255, unique=True)  # Meshy 작업 ID
    status = models.CharField(max_length=50, default="processing")
    created_at = models.DateTimeField(auto_now_add=True)
    create_prompt = models.TextField()  # 생성 프롬프트 (원하는 경우)
    art_style = models.CharField(max_length=50, default="realistic")
    
    
    # Azure Storage에 저장될 파일들 (upload_to는 로컬이 아닌 "Blob 내부 경로"가 됨)
    image_path = models.FileField(blank=True, null=True)
    video_path = models.FileField(blank=True, null=True)
    fbx_path = models.FileField(blank=True, null=True)
    glb_path = models.FileField(blank=True, null=True)
    obj_path = models.FileField(blank=True, null=True)
    usdz_path = models.FileField(blank=True, null=True)
    metadata_path = models.FileField(blank=True, null=True)

    base_color_path = models.FileField(blank=True, null=True)

    def __str__(self):
        return f"Mesh {self.job_id} - {self.status}"


class EnhancedPrompt(models.Model):
    """
    LLM으로 개선된 프롬프트를 저장하는 모델입니다.
    원본 프롬프트, 개선된 프롬프트 목록, 최종 선택된 프롬프트 등을 저장합니다.
    """
    # 관계
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name="enhanced_prompts"
    )
    mesh_prompt = models.ForeignKey(
        MeshPromptModel, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name="enhanced_versions"
    )
    
    # 프롬프트 정보
    original_prompt = models.TextField(help_text="사용자가 입력한 원본 프롬프트")
    enhanced_prompts = models.TextField(help_text="LLM으로 개선된 프롬프트 목록 (JSON)")
    selected_prompt = models.TextField(help_text="최종 선택된 개선 프롬프트")
    selection_reason = models.TextField(blank=True, help_text="프롬프트 선택 이유")
    scores = models.TextField(blank=True, help_text="프롬프트 평가 점수 (JSON)")
    
    # 메타데이터
    created_at = models.DateTimeField(auto_now_add=True)
    used_for_generation = models.BooleanField(default=False, help_text="3D 모델 생성에 사용되었는지 여부")
    
    class Meta:
        verbose_name = "개선된 프롬프트"
        verbose_name_plural = "개선된 프롬프트들"
        ordering = ["-created_at"]
        
    def __str__(self):
        return f"개선된 프롬프트 {self.id} - {self.original_prompt[:30]}..."