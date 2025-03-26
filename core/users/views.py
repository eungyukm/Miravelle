from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from .forms import CustomAuthenticationForm, CustomUserCreationForm
from django.contrib import messages
from urllib.parse import urlparse


# 회원가입
def Register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)   # 바인딩 form
        if form.is_valid():
            user = form.save()
            # 회원가입 완료 후 로그인 페이지로 ID 값을 전달, 250326 추가
            username = form.cleaned_data.get('username')
            return redirect(f"/users/login/?username={username}")  # 쿼리 파라미터로 username 전달 250326 추가
    else:
        form = CustomUserCreationForm()
    return render(request, "register.html", {'form': form}) # 250326 수정


def is_safe_url(url):
    parsed_url = urlparse(url)
    return parsed_url.scheme in ['http', 'https']

# 로그인
def login(request):
    username = request.GET.get('username', '')  # 쿼리 파라미터에서 username 가져오기
    if request.method == "POST":
        form = CustomAuthenticationForm(data=request.POST) # CustomAuthenticationForm 사용
        if form.is_valid():
            user = form.get_user()
            # Log the user in
            auth_login(request, user())   # 로그인 하기
            
            # 'next' 파라미터를 안전하게 처리
            next_url = request.GET.get('next')
            if next_url:
                # next_url이 안전한 URL인지 확인하는 것이 중요 (보안상의 이유).
                # is_safe_url()을 사용하여 도메인이 우리 사이트 내에 있는지 확인.
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
        form = CustomAuthenticationForm(initial={'username': username})  # ID를 initial 값으로 전달 250326 추가
    context = {"form": form, 'next': request.GET.get('next', '')} # next 값을 템플릿에 전달
    return render(request, "login.html", context)


# 로그아웃
@login_required
def logout(request):
    if 'user_id' in request.session:
        del request.session['user_id']  # 세션에서 user_id 삭제
        
    auth_logout(request)    # 로그아웃 하기
    return redirect("articles:main")