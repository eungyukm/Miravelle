from django.urls import path
import workspace.views as views

urlpatterns = [
    path("create/", views.create_mesh_page, name="create_mesh_page"),
    path("meshes/", views.create_mesh, name="create_mesh"),
    path("<str:mesh_id>/", views.get_mesh, name="get_mesh"),
    path("<str:mesh_id>/preview/", views.preview_mesh_page, name="preview_mesh_page"),  # ✅ HTML 렌더링용 뷰 사용
    path("<str:mesh_id>/refine/", views.refine_mesh, name="refine_mesh"),
]