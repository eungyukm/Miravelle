from django.urls import path
from .views import get_image_url

urlpatterns = [
    path("get_image_url/", get_image_url, name="get_image_url"),
]
