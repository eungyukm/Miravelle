from django.urls import path
from .views import GeneratePromptAPI

app_name="prompts"

urlpatterns = [
    path("", GeneratePromptAPI.as_view(), name="generate-prompt-api"),
]
