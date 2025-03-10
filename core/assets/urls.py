from django.contrib import admin
from django.urls import path
from .views import (
    AssetListView, 
    delete_asset,
    create_asset,
    delete_mesh_asset
)

app_name = 'assets'

urlpatterns = [
    path('', AssetListView.as_view(), name='asset_list'),
    path('create/', create_asset, name='asset_create'),  # 에셋 생성 페이지
    path('<int:pk>/delete/', delete_asset, name='asset_delete'),
    path('mesh/<str:job_id>/delete/', delete_mesh_asset, name='mesh_asset_delete'),
]
