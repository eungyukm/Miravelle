from django.urls import path
from . import views

app_name = "workspace"  # ✅ namespace 유지

urlpatterns = [
    path("", views.create_mesh_page, name="create_mesh_page"),  # 🔹 페이지 렌더링
    path("api/generate_mesh/", views.generate_mesh, name="generate_mesh"),  # 🔹 모델 생성 요청 API
    path("<str:mesh_id>/", views.get_mesh, name="get_mesh"),  # 🔹 생성 완료 후 모델 데이터 가져오기
    path("<str:mesh_id>/stream/", views.stream_mesh_progress, name="stream_mesh_progress"),  # 🔹 진행률 스트리밍
]