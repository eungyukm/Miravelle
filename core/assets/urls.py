from django.contrib import admin
from django.urls import path
from .views import (
    AssetListView, 
    delete_mesh_asset,
    publish_to_community
)

app_name = 'assets'

urlpatterns = [
    path('', AssetListView.as_view(), name='asset_list'),
    path('mesh/<str:job_id>/delete/', delete_mesh_asset, name='mesh_asset_delete'),
    path('mesh/<str:job_id>/publish/', publish_to_community, name='publish_to_community'),
]
