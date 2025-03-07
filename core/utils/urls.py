from django.urls import path
from . import views

app_name = 'utils'
urlpatterns = [
    path('list_files/', views.list_files_view, name='list_files'),
    path('check_file/<str:blob_name>/', views.check_file_view, name='check_file'),
    path('upload_file/', views.upload_file_view, name='upload_file'),
    path('delete_file/<str:blob_name>/', views.delete_file_view, name='delete_file'),
    # 추가 코드
    path('list_files_details/', views.list_files_details, name='list_files_details'),
    path('download/<str:file_path>/', views.download_file, name='download_file'),
]