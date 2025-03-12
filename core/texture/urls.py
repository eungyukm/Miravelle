from django.urls import path
from .views import upload_model, check_status

urlpatterns = [
    path("upload/", upload_model, name="upload-model"),
    path("status/<int:texture_id>/", check_status, name="check-status"),
]
