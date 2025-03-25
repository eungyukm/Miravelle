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
            
            # 'next' 파라미터를 안전하게 처리
            next_url = request.GET.get('next')
            if next_url:
                # next_url이 안전한 URL인지 확인하는 것이 중요 (보안상의 이유).
                # is_safe_url()을 사용하여 도메인이 우리 사이트 내에 있는지 확인합니다.
                from django.utils.http import is_safe_url
                if is_safe_url(url=next_url, allowed_hosts=request.get_host()):
                    return redirect(next_url)
                else:
                    # 안전하지 않은 URL인 경우, 기본 URL로 리디렉션
                    return redirect("articles:main")
            else:
                return redirect("articles:main")
            
        else:
            # 유효하지 않을 경우, 오류 메시지 추가
            messages.error(request, "Invalid ID or Password.")
    else:    
        form = CustomAuthenticationForm()  # CustomAuthenticationForm 사용
    context = {"form": form, 'next': request.GET.get('next', '')} # next 값을 템플릿에 전달
    return render(request, "login.html", context)


# 로그아웃
@login_required
def logout(request):
    if 'user_id' in request.session:
        del request.session['user_id']  # 세션에서 user_id 삭제
        
    auth_logout(request)    # 로그아웃 하기
    return redirect("articles:main")