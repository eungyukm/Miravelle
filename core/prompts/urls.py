from django.urls import path
from .views import GeneratePromptAPI, EnhancePromptAPI

app_name="prompts"

urlpatterns = [
    path('', GeneratePromptAPI.as_view(), name='generate-prompt-api'),
    path('enhance/', EnhancePromptAPI.as_view(), name='enhance-prompt'),
]
