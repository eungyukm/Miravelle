from django.shortcuts import render

def three_world_view(request):
    return render(request, 'threeworld/shader.html')
    return render(request, 'threeworld/index.html')