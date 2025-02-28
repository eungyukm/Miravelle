from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages

# login View
def login_view(request):
    return render(request, 'login.html')
