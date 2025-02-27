from django.urls import path, include
from .views import login_view

urlpatterns = [
    path('', login_view, name='hello_world'),
]