from django.urls import path
from .views import ArticleList

app_name = "articles"
urlpatterns = [
    path("articlelist/", ArticleList, name="articlelist"), # 게시물 목록
]
