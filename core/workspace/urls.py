from django.urls import path
from .views import (
    create_mesh_page,
    create_mesh,
    get_mesh,
    preview_mesh,  # ✅ preview_mesh_api → preview_mesh로 변경
    preview_mesh_page,
    refine_mesh
)

urlpatterns = [
    path("create/", create_mesh_page, name="create_mesh_page"),
    path("create/api/", create_mesh, name="create_mesh"),
    path("<str:mesh_id>/", get_mesh, name="get_mesh"),
    path("<str:mesh_id>/preview/", preview_mesh, name="preview_mesh"),  # ✅ HTML 렌더링 뷰로 변경!
    path("preview/<str:job_id>/", preview_mesh_page, name="preview_mesh_page"),
    path("<str:mesh_id>/refine/", refine_mesh, name="refine_mesh"),
]
