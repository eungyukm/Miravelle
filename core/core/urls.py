from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Swagger 스키마 설정
schema_view = get_schema_view(
    openapi.Info(
        title="API Documentation",
        default_version='v1',
        description="API documentation",
        terms_of_service="https://www.google.com/policies/terms/",
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("users/", include("users.urls")),
    path("assets/", include("assets.urls")),
    path("workspace/", include("workspace.urls")),
    path("article/", include("articles.urls")),
    path("threeworld/", include("threeworld.urls")),
    path("utils/", include("utils.urls")),
    path("texture/", include("texture.urls")),
    path("api/prompts/", include("prompts.urls")),


    path("publish/", include("model_storage.urls")),

    # rest_framework
    path("api/v1/", include("api_v1.urls")),
    path("api/v1/vision/", include("vision.urls")),
    
    # main page
    path("", include("articles.urls")),

    # Swagger UI
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    # ReDoc UI
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    # JSON Schema
    path('swagger.json/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) #유저가 업로드한 파일들을 가져오는 경로

SWAGGER_SETTINGS = {
    'SECURE_SCHEMA': 'https',  # HTTP가 아닌 HTTPS 사용
    'USE_SESSION_AUTH': False,
    'PERSIST_AUTH': True,
}