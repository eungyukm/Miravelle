from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from .forms import CustomAuthenticationForm, CustomUserCreationForm
from django.urls import reverse

# 메인 화면
def main(request):
    return render(request, "main.html")


# 회원가입
def Register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)   # 바인딩 form
        if form.is_valid():
            user = form.save()
            # 로그인 페이지 URL을 가져옴
            login_url = reverse("users:login")
            return redirect(login_url)
    else:
        form = CustomUserCreationForm()
    context = {'form': form}
    return render(request, "register.html", context)


# 로그인
def login(request):
    if request.method == "POST":
        form = CustomAuthenticationForm(data=request.POST) # CustomAuthenticationForm 사용
        if form.is_valid():
            # Log the user in
            auth_login(request, form.get_user())   # 로그인 하기
            return redirect("users:main")
    
    else:    
        form = CustomAuthenticationForm()  # CustomAuthenticationForm 사용
    context = {"form": form}
    return render(request, "login.html", context)


# 로그아웃
@login_required
def logout(request):
    auth_logout(request)    # 로그아웃 하기
    return redirect("users:main")