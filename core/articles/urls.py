from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from .views import ArticleList, ArticleLike, ArticleCreate, ArticleDetail

app_name = "articles"
urlpatterns = [
    path("", ArticleList.as_view(), name="main"), # 게시물 목록
    # article_id와 like_type을 URL 피라미터로 받음 ⬇️
    path("articles/<int:id>/like/<str:like_type>/", ArticleLike.as_view(), name="articlelike"),
    path("create/", ArticleCreate.as_view(), name="articlecreate"), # 게시물 생성
    path("<int:pk>/", ArticleDetail.as_view(), name="articledetail"), # 게시물 상세보기
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

