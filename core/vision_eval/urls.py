from django.urls import path
from .views import get_image_url, get_evaluation_image

urlpatterns = [
    path("get-image-url/", get_image_url, name="get_image_url"),
    path("image/evaluate/", get_evaluation_image, name="get_evaluation_image"),
]
