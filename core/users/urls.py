from django.urls import path
from .views import main, Register, login, logout

app_name = "users"
urlpatterns = [
    path("main/", main, name="main"), # 메인 화면
    path("register/", Register, name="register" ), # 회원 가입
    path("login/", login, name="login"), # 로그인
    path("logout/", logout, name="logout"), # 로그아웃
]