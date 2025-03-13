from django.urls import path
from .views import model_texture_form, check_status, model_texture_submit, texture_status_stream
from .views import text_to_texture, check_texture_status, texuring_streaming

urlpatterns = [
    path("model_texture_form/", model_texture_form, name="model_texture_form"),
    path("model_texture_submit/", model_texture_submit, name="model_texture_submit"),
    path('status/<str:task_id>/', check_status, name='check_status'),
    path('stream/<str:task_id>/', texture_status_stream, name='texture_status_stream'),

    # Testing API
    path("text_to_texture/", text_to_texture, name="text_to_texture"),
    path("check_texture_status/", check_texture_status, name="tcheck_texture_status"),
    path("texuring_streaming/", texuring_streaming, name="texuring_streaming"),
]
