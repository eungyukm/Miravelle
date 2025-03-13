from django.urls import path
from .views import MeshyTextTo3DView, Generate3DView, List3DModelsView

urlpatterns = [
    path('text-to-3d/<str:task_id>/', MeshyTextTo3DView.as_view(), name='meshy-text-to-3d'),
    path('generate-3d/', Generate3DView.as_view(), name='generate-3d'),
    path('list-3d-models/', List3DModelsView.as_view(), name='list-3d-models'),
]