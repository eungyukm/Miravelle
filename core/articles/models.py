from django.db import models
from django.conf import settings
from workspace.models import MeshModel
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
"""
아래 내용을 포함하고 있어요.
user id, job id, title, model&texture_prompt, model_seed, image, likes, dislikes, created_at, tag

model_seed : 랜덤으로 1 ~ 2147483648 숫자 범위 내에서 부여됩니다.
-> def save, def generate_unique_model_seed로 저장 및 유니크 관리

"""
class Article(models.Model):
    user_id = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="articles"
        ) # 유저 아이디
    job_id = models.ForeignKey(MeshModel, on_delete=models.CASCADE) # 작업 아이디
    title = models.CharField(max_length=255, default="model_prompt") # 게시글 제목
    model_prompt = models.TextField()
    texture_prompt = models.TextField()
    model_seed = models.IntegerField(unique=True)
    image = models.ImageField(upload_to="article/image/") # 모델 이미지
    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="like_articles"
    ) # 좋아요
    dislikes = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="dislike_articles"
    ) # 싫어요
    created_at = models.DateTimeField(auto_now_add=True) # 생성 시간
    tags = models.CharField
    
    # model_seed는 정한 범위값 내에서 랜덤으로 부여(중복 허용 X)
    def save(self, *args, **kwargs):
        if not self.model_seed:  # 값이 없을 때만 생성
            self.model_seed = self.generate_unique_model_seed()
        super().save(*args, **kwargs)

    def generate_unique_model_seed(self):
        while True:
            number = random.randint(1, 2147483648)  # 원하는 범위 설정
            if not Article.objects.filter(model_seed=number).exists():
                return number