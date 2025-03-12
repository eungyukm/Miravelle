from django.urls import path
from .views import model_texture_form, check_status, model_texture_submit
from .views import text_to_texture, check_texture_status, texuring_streaming

urlpatterns = [
    path("model_texture_form/", model_texture_form, name="model_texture_form"),
    path("model_texture_submit/", model_texture_submit, name="model_texture_submit"),
    path("status/<uuid:texture_id>/", check_status, name="check-status"),

    # Testing API
    path("text_to_texture/", text_to_texture, name="text_to_texture"),
    path("check_texture_status/", check_texture_status, name="test-status"),
    path("texuring_streaming/", texuring_streaming, name="texuring_streaming"),
]
