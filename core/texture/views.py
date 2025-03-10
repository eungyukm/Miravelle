from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .utils import call_meshy_api

@csrf_exempt
def TextureCreate(request):
    return render(request, "/Users/baeminkyung/Desktop/Miravelle/core/workspace/templates/workspace/create_mesh.html")
