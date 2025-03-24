from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from .forms import CustomAuthenticationForm, CustomUserCreationForm
from django.urls import reverse
from django.contrib import messages


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
            user = form.get_user()
            # Log the user in
            auth_login(request, form.get_user())   # 로그인 하기
            request.session['user_id'] = user.id  # 세션에 user.id 저장
            
            # 'next' 파라미터를 확인하고, 존재하면 해당 URL로, 없으면 'articles:main'으로 리디렉션
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            else:
                return redirect("articles:main")
            
        else:
            # 유효하지 않을 경우, 오류 메시지 추가
            messages.error(request, "Invalid ID or Password.")
    else:    
        form = CustomAuthenticationForm()  # CustomAuthenticationForm 사용
    context = {"form": form}
    return render(request, "login.html", context)


# 로그아웃
@login_required
def logout(request):
    if 'user_id' in request.session:
        del request.session['user_id']  # 세션에서 user_id 삭제
        
    auth_logout(request)    # 로그아웃 하기
    return redirect("articles:main")