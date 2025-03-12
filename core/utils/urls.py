from django.urls import path
from .views import list_files_details, list_files_view, check_file_view, upload_file_view, delete_file_view
from django.urls import path
from .views import list_files_view
from .views import list_files_view, check_file_view, upload_file_view, delete_file_view
from .views import get_glb_file

urlpatterns = [
    path('list_files/', list_files_view, name='list_files'),
    path('check_file/<str:blob_name>/', check_file_view, name='check_file'),
    path('upload_file/', upload_file_view, name='upload_file'),
    path('delete_file/<str:blob_name>/', delete_file_view, name='delete_file'),

    path('get_glb/<uuid:file_id>/', get_glb_file, name='get_glb_file'),
]