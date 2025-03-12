from django.db import models
from django.conf import settings
from workspace.models import MeshModel
from users.models import User
import random

"""
3월 5일까지
게시글 겉에 보일 것들 : 
- 생성된 모델 사진 
- 유저 id
- 작업 id
- 좋아요, 싫어요 버튼

3월 5일 이후로 할 것들 ⬇️
게시글 상세 내용 :
(왼편)
- 생성된 모델 사진
- 타이틀 (모델 프롬프트)
- 태그
- 모델 시드 (pk)
- 모델 프롬프트 (복사 버튼)
- 텍스쳐 프롬프트 (복사 버튼)

(오른편)- 추후 추가할지 말지 결정하자.
- 유저 프로필
- 팔로우 버튼
- 유저의 다른 모델 작품 리스트(미리보기, 모델 프롬프트) -> 추후
"""


# article 모델
class Article(models.Model):
    """
    아래 내용을 포함하고 있어요.
    게시물 id, user id, job id, title, model&texture_prompt,
    model_seed, image, likes&dislikes 개수, created_at, tag

    model_seed : 랜덤으로 1 ~ 2147483648 숫자 범위 내에서 부여됩니다.
    -> def save, def generate_unique_model_seed로 저장 및 유니크 관리
    """
    id = models.AutoField(primary_key=True)
    image = models.ImageField(upload_to="article/image/") # 모델 이미지
    like_count = models.PositiveIntegerField(default=0) # 좋아요 개수
    dislike_count = models.PositiveIntegerField(default=0) # 싫어요 개수
    user_id = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="articles"
        ) # 유저 아이디
    title = models.CharField(max_length=255) # 게시글 제목
    created_at = models.DateTimeField(auto_now_add=True) # 생성 시간
    tags = models.CharField(max_length=100, blank=True)
    model_prompt = models.TextField()
    texture_prompt = models.TextField()
    model_seed = models.IntegerField(unique=True) # 타이틀의 고유 번호

    job = models.OneToOneField(
        MeshModel,
        on_delete=models.CASCADE,
        related_name='article',
        null=True,
        blank=True
    )

    status = models.CharField(max_length=50, default="processing")
    create_prompt = models.TextField(blank=True, null=True)
    image_path = models.FileField(blank=True, null=True)
    video_path = models.FileField(blank=True, null=True)
    fbx_path = models.FileField(blank=True, null=True)
    glb_path = models.FileField(blank=True, null=True)
    obj_path = models.FileField(blank=True, null=True)
    usdz_path = models.FileField(blank=True, null=True)
    metadata_path = models.FileField(blank=True, null=True)

    
    
    # model_seed는 정한 범위값 내에서 랜덤으로 부여(중복 허용 X)
    def save(self, *args, **kwargs):
        if not self.model_seed:
            self.model_seed = self.generate_unique_model_seed()

        if self.job:
            self.status = self.job.status
            self.create_prompt = self.job.create_prompt
            self.image_path = self.job.image_path
            self.video_path = self.job.video_path
            self.fbx_path = self.job.fbx_path
            self.glb_path = self.job.glb_path
            self.obj_path = self.job.obj_path
            self.usdz_path = self.job.usdz_path
            self.metadata_path = self.job.metadata_path

        super().save(*args, **kwargs)

    def generate_unique_model_seed(self):
        while True:
            number = random.randint(1, 2147483648)  # 원하는 범위 설정
            if not Article.objects.filter(model_seed=number).exists():
                return number
            
    def __str__(self):
        return f"{self.title} - {self.status}"
    
# Like 모델
class Like(models.Model):
    """
    유저가 게시글에 좋아요/싫어요 누른 정보를 저장하는 모델이에요.
    """
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_likes"
    )
    article = models.ForeignKey(
        Article, on_delete=models.CASCADE, related_name="article_likes"
    )
    like_type = models.CharField(
        max_length=10, choices=(("❤️", "like"), ("🤨", "dislike"))
    )
    
    # 유저-게시글 조합은 유일해야 함. 중복 좋아요 방지
    class Meta :
        unique_together = ("user", "article")
        
    def __str__(self):
        return f"{self.user.username} - {self.article.title} - {self.like_type}"