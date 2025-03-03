from django.shortcuts import render
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Asset

# Create your views here.

class AssetListView(LoginRequiredMixin, ListView):
    model = Asset
    template_name = 'assets/asset_list.html'
    context_object_name = 'assets'
    
    def get_queryset(self):
        return Asset.objects.filter(user=self.request.user)
