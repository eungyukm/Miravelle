from django.contrib import admin
from .models import TestMeshModel, TestMeshAsset

admin.site.register(TestMeshModel)
admin.site.register(TestMeshAsset)
