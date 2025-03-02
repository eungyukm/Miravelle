from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm
from django.contrib.auth import login as auth_login

# 회원가입
def Register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)   # 바인딩 form
        if form.is_valid():
            user = form.save()
            auth_login(request, user) # 로그인 하기
            return redirect("main")
    else:
        form = CustomUserCreationForm()
    context = {'form': form}
    return render(request, "accounts/register.html", context)