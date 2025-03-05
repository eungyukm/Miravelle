from django.contrib import admin
from django.urls import path
from .views import (
    AssetListView, 
    AssetDetailView, 
    test_create_asset, 
    delete_asset,
    update_asset
)

app_name = 'assets'

urlpatterns = [
    path('', AssetListView.as_view(), name='asset_list'),
    path('<int:pk>/', AssetDetailView.as_view(), name='asset_detail'),
    path('<int:pk>/edit/', update_asset, name='asset_edit'),  # 수정 URL
    path('<int:pk>/delete/', delete_asset, name='asset_delete'),
    path('test/create/', test_create_asset, name='test_create_asset'),  # 테스트용 URL
]
