from django.urls import path, include
from .views import login, logout

urlpatterns = [
    path('login/', login, name='login'), # 로그인
    path('logout/', logout, name='logout'), # 로그아웃
]