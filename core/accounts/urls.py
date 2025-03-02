from django.conf import urls
from django.urls import path
from . import views


urlpatterns = [
    path("register/", views.Register, name="register" ) # 회원 가입
]
