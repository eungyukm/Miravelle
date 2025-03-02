from django.urls import path, include
from .views import login

urlpatterns = [
    path('login/', login, name='login'),
]