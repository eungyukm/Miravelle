from django.shortcuts import render
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Asset

# Create your views here.

class AssetListView(LoginRequiredMixin, ListView):
    model = Asset # 모델 지정
    template_name = 'assets/asset_list.html' # 템플릿 지정
    context_object_name = 'assets' # 컨텍스트 객체 이름 지정
    
    def get_queryset(self):
        return Asset.objects.filter(user=self.request.user) # 에셋 모델에서 필터링, 유저 자신의 에셋만 조회
