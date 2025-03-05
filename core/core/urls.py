from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("users/", include('users.urls')),
    path("assets/", include('assets.urls')),
    path("workspace/", include('workspace.urls')),
    path("article/", include('articles.urls')),
    path("threeworld/", include("threeworld.urls")),
    path("utils/", include("utils.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) #유저가 업로드한 파일들을 가져오는 경로

