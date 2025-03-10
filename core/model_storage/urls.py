from django.urls import path
from .views import first_publish, publish_article

urlpatterns = [
    # 첫 번째 MeshModel을 기반으로 Article 생성
    path("first/", first_publish, name='first_publish'),

    # 특정 MeshModel을 기반으로 Article 생성
    path("articles/<int:id>/", publish_article, name='publish_article'),
]