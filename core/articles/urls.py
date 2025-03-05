from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from .views import ArticleList, ArticleLike

app_name = "articles"
urlpatterns = [
    path("articles/", ArticleList.as_view(), name="articlelist"), # 게시물 목록
    # article_id와 like_type을 URL 피라미터로 받음 ⬇️
    path("articles/<int:article_id>/like/<str:like_type>/", ArticleLike.as_view(), name="articlelike")
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

