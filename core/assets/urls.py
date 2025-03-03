from django.contrib import admin
from django.urls import path
from .views import AssetListView

app_name = 'assets'

urlpatterns = [
    path('', AssetListView.as_view(), name='asset_list'),
]
