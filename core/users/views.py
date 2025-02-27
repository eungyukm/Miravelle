from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

@login_required
def hello_world(request):
    return HttpResponse("Hello, World!")
