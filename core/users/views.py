from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required

# 로그인
def login(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            # Log the user in
            auth_login(request, form.get_user())   # 로그인 하기
            next_url = request.GET.get("next") or "main"
            return redirect(next_url)
    
    else:    
        form = AuthenticationForm()
    context = {'form': form}
    return render(request, 'login.html', context)


# 로그아웃
@login_required
def logout(request):
    auth_logout(request)    # 로그아웃 하기
    return redirect('main')