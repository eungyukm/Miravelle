from django.urls import path
from .views import MeshyTextTo3DView

urlpatterns = [
    path('text-to-3d/<str:task_id>/', MeshyTextTo3DView.as_view(), name='meshy-text-to-3d'),
]