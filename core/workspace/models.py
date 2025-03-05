from django.conf import settings
from django.db import models
from workspace.azure_utils import upload_file_to_azure


class MeshModel(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # 유저 정보
    job_id = models.CharField(max_length=255, unique=True)  # Meshy 작업 ID
    status = models.CharField(max_length=50, default="processing")  # 모델 상태
    created_at = models.DateTimeField(auto_now_add=True)  # 생성 날짜
    create_prompt = models.TextField()  # 생성 프롬프트 저장

    # 원본 URL (Meshy API에서 받은 URL)
    image_url = models.URLField(blank=True, null=True)  
    video_url = models.URLField(blank=True, null=True)  
    fbx_url = models.URLField(blank=True, null=True)  

    # Azure Storage에 저장된 파일 경로
    image_path = models.FileField(upload_to="meshes/images/", blank=True, null=True)  
    video_path = models.FileField(upload_to="meshes/videos/", blank=True, null=True)  
    fbx_path = models.FileField(upload_to="meshes/fbx/", blank=True, null=True)  

    def __str__(self):
        return f"Mesh {self.job_id} - {self.status}"

    def upload_assets_to_azure(self):
        """ Meshy에서 받은 URL을 Azure에 업로드 후 저장 """
        updated = False  # 변경 여부 체크
        
        if self.image_url and not self.image_path:
            image_file_name = f"{self.job_id}.png"
            image_blob_url = upload_file_to_azure(self.image_url, self.job_id, "images", image_file_name)
            if "upload failed" not in image_blob_url:
                self.image_path = image_blob_url
                updated = True

        if self.video_url and not self.video_path:
            video_file_name = f"{self.job_id}.mp4"
            video_blob_url = upload_file_to_azure(self.video_url, self.job_id, "videos", video_file_name)
            if "upload failed" not in video_blob_url:
                self.video_path = video_blob_url
                updated = True

        if self.fbx_url and not self.fbx_path:
            fbx_file_name = f"{self.job_id}.fbx"
            fbx_blob_url = upload_file_to_azure(self.fbx_url, self.job_id, "fbx", fbx_file_name)
            if "upload failed" not in fbx_blob_url:
                self.fbx_path = fbx_blob_url
                updated = True

        if updated:
            self.save()  # 모델 저장