from django.urls import path
from .views import three_world_view

urlpatterns = [
    path('', three_world_view, name='three_world_view'),
]