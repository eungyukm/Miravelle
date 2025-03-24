from django.urls import path
from .views import get_evaluation_image, save_evaluation

urlpatterns = [
    path("image/evaluate/", get_evaluation_image, name="get_evaluation_image"),
    path("image/evaluate/<str:pk>/", save_evaluation, name="save_evaluation"),
]
