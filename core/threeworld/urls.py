from django.urls import path
from .views import three_world_view
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', three_world_view, name='three_world_view'),
]