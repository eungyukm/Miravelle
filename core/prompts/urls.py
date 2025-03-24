from django.urls import path
from .views import GeneratePromptAPI, EnhancePromptAPI

app_name="prompts"

urlpatterns = [
    path('generate/', GeneratePromptAPI.as_view(), name='generate-prompt'),
    path('enhance/', EnhancePromptAPI.as_view(), name='enhance-prompt'),
]
