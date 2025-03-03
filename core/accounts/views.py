from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm
from django.urls import reverse


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
    return render(request, "accounts/register.html", context)