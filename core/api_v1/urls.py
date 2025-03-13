from django.urls import path
from .views import Generate3DPreview, Refine3DPreview, List3DModelsView

urlpatterns = [
    path("generate/<str:task_id>/", Generate3DPreview.as_view(), name="generate-3d-preview"),
    path("refine/", Refine3DPreview.as_view(), name="refine-3d-preview"),
    path("list/", List3DModelsView.as_view(), name="list-3d-preview"),
]