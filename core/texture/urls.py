from django.urls import path
from .views import TextureCreate


app_name = "texture"
urlpatterns = [
    path("", TextureCreate, name="texture-create"), # 텍스처 생성
]
