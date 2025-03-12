from django.urls import path
from .views import upload_model, check_status, text_to_texture, check_texture_status

urlpatterns = [
    path("upload/", upload_model, name="upload-model"),
    path("status/<uuid:texture_id>/", check_status, name="check-status"),

    # Testing API
    path("text_to_texture/", text_to_texture, name="text_to_texture"),
    path("check_texture_status/", check_texture_status, name="test-status"),
]
