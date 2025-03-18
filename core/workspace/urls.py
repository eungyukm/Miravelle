from django.urls import path
from . import views

app_name = "workspace"  # namespace 유지

urlpatterns = [
    path("", views.create_mesh_page, name="create_mesh_page"),  # 페이지 렌더링

    path("check_status/", views.check_status, name="check_status"),
    path("check_refine_mesh_status/", views.check_refine_mesh_status, name="check_refine_mesh_status"),

    path("api/generate_mesh/", views.generate_mesh, name="generate_mesh"),  # 모델 생성 요청 API
    path("<str:mesh_id>/", views.get_mesh, name="get_mesh"),  # 생성 완료 후 모델 데이터 가져오기
    path("<str:mesh_id>/stream/", views.stream_mesh_progress, name="stream_mesh_progress"),  # 진행률 스트리밍

    path("refine_mesh", views.refine_mesh, name="refine_mesh"),
    path("<str:mesh_id>/refine_stream/", views.stream_refine_mesh_progress, name="stream_refine_mesh_progress"),

    # refined mesh 정보를 가져오는 API 엔드포인트
    path("<str:mesh_id>/get_refine_mesh/", views.get_refine_mesh, name="get_refine_mesh"),
]