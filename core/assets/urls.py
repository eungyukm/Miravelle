from django.contrib import admin
from django.urls import path
from .views import (
    AssetListView, 
    delete_asset,
    create_asset
)

app_name = 'assets'

urlpatterns = [
    path('', AssetListView.as_view(), name='asset_list'),
    path('create/', create_asset, name='asset_create'),  # 에셋 생성 페이지
    path('<int:pk>/delete/', delete_asset, name='asset_delete'),
]
