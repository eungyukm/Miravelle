from django.urls import path, include
from .views import hello_world

urlpatterns = [
    path('users/', hello_world, name='hello_world'),
]