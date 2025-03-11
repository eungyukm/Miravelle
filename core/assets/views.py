from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils import timezone
from datetime import timedelta, datetime
from workspace.models import MeshModel
from .models import MeshAsset
from utils.azure_key_manager import AzureKeyManager
from azure.storage.blob import generate_blob_sas, BlobSasPermissions, BlobServiceClient
import requests
import logging
import json
import os

# 로깅 설정
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# AzureKeyManager 인스턴스 가져오기
azure_keys = AzureKeyManager.get_instance()

def generate_sas_token(blob_name):
    """
    Azure Blob Storage의 특정 파일에 대한 SAS 토큰 생성
    
    Args:
        blob_name: SAS 토큰을 생성할 Blob 이름
        
    Returns:
        str: SAS 토큰 문자열
    """
    try:
        # AzureKeyManager에서 키 가져오기
        storage_account_name = azure_keys.storage_account_name
        storage_account_key = azure_keys.storage_account_key
        container_name = azure_keys.container_name
        
        logger.info(f"SAS 토큰 생성 시도: storage_account_name={storage_account_name}, container_name={container_name}")
        logger.info(f"storage_account_key 존재 여부: {bool(storage_account_key)}")
        
        if not storage_account_key:
            logger.warning("Azure Storage 계정 키를 찾을 수 없습니다. SAS 토큰 생성이 불가능합니다.")
            # 클라우드 환경에서는 공개 URL 반환
            return ""
        
        # SAS 토큰 생성 (1시간 유효)
        sas_token = generate_blob_sas(
            account_name=storage_account_name,
            container_name=container_name,
            blob_name=blob_name,
            account_key=storage_account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1)
        )
        
        logger.info(f"SAS 토큰 생성 성공: {blob_name}")
        return sas_token
    except Exception as e:
        logger.error(f"SAS 토큰 생성 실패: {str(e)}")
        return ""

def check_file_exists(blob_name):
    """Azure Blob Storage에서 특정 파일 존재 여부 확인"""
    try:
        # AzureKeyManager에서 키 가져오기
        storage_account_name = azure_keys.storage_account_name
        storage_account_key = azure_keys.storage_account_key
        container_name = azure_keys.container_name
        
        logger.info(f"파일 존재 확인 시도: storage_account_name={storage_account_name}, container_name={container_name}")
        logger.info(f"storage_account_key 존재 여부: {bool(storage_account_key)}")
        
        if not storage_account_key:
            logger.warning("Azure Storage 계정 키를 찾을 수 없습니다. 파일 존재 여부 확인이 불가능합니다.")
            # 클라우드 환경에서는 파일이 존재한다고 가정
            return True
        
        # Blob Service Client 생성
        blob_service_client = BlobServiceClient(
            account_url=f"https://{storage_account_name}.blob.core.windows.net",
            credential=storage_account_key
        )
        
        # 컨테이너에서 파일 존재 여부 확인
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        exists = blob_client.exists()
        logger.info(f"파일 {blob_name} 존재 여부: {exists} (컨테이너: {container_name})")
        return exists
    except Exception as e:
        logger.error(f"파일 존재 여부 확인 실패: {str(e)}")
        # 클라우드 환경에서는 파일이 존재한다고 가정
        return True

def verify_blob_exists(blob_path):
    """Azure Blob Storage에서 파일이 실제로 존재하는지 확인"""
    try:
        # AzureKeyManager에서 키 가져오기
        storage_account_name = azure_keys.storage_account_name
        storage_account_key = azure_keys.storage_account_key
        container_name = azure_keys.container_name
        
        if not storage_account_key:
            logger.warning("Azure Storage 계정 키를 찾을 수 없습니다. 파일 존재 여부 확인이 불가능합니다.")
            return False
        
        # Blob Service Client 생성
        blob_service_client = BlobServiceClient(
            account_url=f"https://{storage_account_name}.blob.core.windows.net",
            credential=storage_account_key
        )
        
        # 컨테이너에서 파일 존재 여부 확인
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_path)
        exists = blob_client.exists()
        logger.info(f"파일 {blob_path} 존재 여부: {exists} (컨테이너: {container_name})")
        return exists
    except Exception as e:
        logger.error(f"파일 존재 여부 확인 실패: {str(e)}")
        return False

class AssetListView(LoginRequiredMixin, ListView):
    """
    사용자의 3D 모델 에셋 목록을 보여주는 뷰
    - MeshModel에서 생성된 에셋만 표시
    """
    model = MeshAsset
    template_name = 'assets/asset_list.html'
    context_object_name = 'mesh_assets'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 사용자의 MeshModel에 해당하는 MeshAsset 가져오기
        mesh_models = MeshModel.objects.filter(user=self.request.user)
        mesh_assets = []
        
        for mesh_model in mesh_models:
            # MeshAsset이 없으면 생성
            asset, created = MeshAsset.objects.get_or_create(
                mesh_model=mesh_model,
                defaults={
                    'title': f'Mesh {mesh_model.job_id[:8]}',
                    'prompt': mesh_model.create_prompt,  # 생성 시 프롬프트 설정
                }
            )
            
            # 항상 URL 업데이트 (last_url_update 필드 사용하지 않음)
            try:
                # 직접 URL 업데이트
                job_id = mesh_model.job_id
                
                # 디버깅을 위한 로깅 추가
                logger.info(f"MeshModel 정보: job_id={job_id}, image_path={mesh_model.image_path}, fbx_path={mesh_model.fbx_path}")
                
                # 프롬프트 업데이트 (이미 존재하는 에셋의 경우)
                if not asset.prompt and mesh_model.create_prompt:
                    asset.prompt = mesh_model.create_prompt
                
                # 스토리지 계정 이름과 컨테이너 이름 가져오기
                storage_account_name = azure_keys.storage_account_name or "miravelledevstorage"
                container_name = azure_keys.container_name or "meshy-3d-assets"
                
                # 썸네일 파일 경로
                thumbnail_path = f"tasks/{job_id}/previews/preview.png"
                # 실제 파일 존재 여부 확인
                thumbnail_exists = verify_blob_exists(thumbnail_path)
                logger.info(f"썸네일 파일 존재 여부: {thumbnail_exists} (경로: {thumbnail_path})")
                
                # 썸네일 URL 설정
                if mesh_model.image_path and mesh_model.image_path.startswith('http'):
                    # 이미 전체 URL이 저장되어 있으면 그대로 사용
                    asset.thumbnail_url = mesh_model.image_path
                    logger.info(f"MeshModel.image_path 사용: {asset.thumbnail_url}")
                elif thumbnail_exists:
                    # 파일이 존재하면 URL 생성
                    asset.thumbnail_url = f"https://{storage_account_name}.blob.core.windows.net/{container_name}/{thumbnail_path}"
                    logger.info(f"썸네일 URL 생성 (파일 존재): {asset.thumbnail_url}")
                
                # FBX 파일 경로
                fbx_path = f"tasks/{job_id}/models/model.fbx"
                # 실제 파일 존재 여부 확인
                fbx_exists = verify_blob_exists(fbx_path)
                logger.info(f"FBX 파일 존재 여부: {fbx_exists} (경로: {fbx_path})")
                
                # FBX URL 설정
                if mesh_model.fbx_path and mesh_model.fbx_path.startswith('http'):
                    # 이미 전체 URL이 저장되어 있으면 그대로 사용
                    asset.fbx_url = mesh_model.fbx_path
                    logger.info(f"MeshModel.fbx_path 사용: {asset.fbx_url}")
                elif fbx_exists:
                    # 파일이 존재하면 URL 생성
                    asset.fbx_url = f"https://{storage_account_name}.blob.core.windows.net/{container_name}/{fbx_path}"
                    logger.info(f"FBX URL 생성 (파일 존재): {asset.fbx_url}")

                asset.save()
            except Exception as e:
                logger.error(f"Error updating URLs for {asset}: {e}")
            
            mesh_assets.append(asset)
        
        context['mesh_assets'] = mesh_assets
        return context
    
    def get_queryset(self):
        """현재 로그인한 사용자의 MeshModel에 해당하는 MeshAsset만 반환"""
        return MeshAsset.objects.filter(mesh_model__user=self.request.user).order_by('-mesh_model__created_at')

@require_POST
@login_required
def delete_mesh_asset(request, job_id):
    """
    메시 에셋을 삭제하는 뷰
    """
    try:
        mesh_asset = get_object_or_404(MeshAsset, mesh_model__job_id=job_id, mesh_model__user=request.user)
        mesh_model = mesh_asset.mesh_model
        
        # MeshAsset과 MeshModel 모두 삭제
        mesh_asset.delete()
        mesh_model.delete()
        
        return JsonResponse({
            "message": "Asset deleted successfully",
            "job_id": job_id
        })
        
    except Exception as e:
        return JsonResponse({
            "error": str(e)
        }, status=500)


