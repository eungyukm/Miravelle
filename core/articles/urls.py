from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from .views import ArticleList

app_name = "articles"
urlpatterns = [
    path("articlelist/", ArticleList, name="articlelist"), # 게시물 목록
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

