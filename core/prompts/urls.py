from django.urls import path
from .views import GenerateMesh

app_name="prompts"

urlpatterns = [
    path("", GenerateMesh.as_view(), name="generate_mesh"),
]
