from django.db import models
from django.conf import settings

class Asset(models.Model): #     ┌> 사용자 모델을 참조하는 설정                           ┌> = user.assets.all()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='assets') # 사용자와 연결
    title = models.CharField(max_length=200) 
    content = models.TextField(blank=True)

    file_path = models.CharField(max_length=500)  # 3D 파일 경로
    thumbnail = models.ImageField(upload_to='asset_thumbnails/', null=True, blank=True) # 썸네일
    #                   업로드된 이미지 저장 경로 지정, <┘          └> 빈 값 허용, 업로드 안해도 됨

    # 생성일과 수정일 자동 생성
    created_at = models.DateTimeField(auto_now_add=True) # 생성일
    updated_at = models.DateTimeField(auto_now=True) # 수정일
    
    class Meta:
        ordering = ['-created_at'] # 생성일 기준 내림차순 정렬
    
    def __str__(self):
        return f"{self.title} - {self.user.username}" # 제목과 사용자 이름 반환
