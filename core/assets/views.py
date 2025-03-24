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
import requests
import logging
import json
import os
from articles.models import Article  # 추가: Article 모델 임포트

# 로깅 설정
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# AzureKeyManager 인스턴스 가져오기
azure_keys = AzureKeyManager.get_instance()

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
                # AzureKeyManager에서 가져오지 못할 경우 하드코딩된 값 사용
                storage_account_name = azure_keys.storage_account_name
                container_name = azure_keys.container_name
                
                # 값이 없으면 하드코딩된 값 사용
                if not storage_account_name:
                    storage_account_name = "miravelledevstorage"
                    logger.info(f"AzureKeyManager에서 storage_account_name을 가져오지 못해 하드코딩된 값 사용: {storage_account_name}")
                
                if not container_name:
                    container_name = "meshy-3d-assets"
                    logger.info(f"AzureKeyManager에서 container_name을 가져오지 못해 하드코딩된 값 사용: {container_name}")
                
                # 썸네일 URL 생성 (SAS 토큰 없이 공개 URL 사용)
                thumbnail_url = f"https://{storage_account_name}.blob.core.windows.net/{container_name}/tasks/{job_id}/previews/preview.png"
                asset.thumbnail_url = thumbnail_url
                logger.info(f"썸네일 URL 생성: {thumbnail_url}")
                
                # FBX URL 생성 (SAS 토큰 없이 공개 URL 사용)
                fbx_url = f"https://{storage_account_name}.blob.core.windows.net/{container_name}/tasks/{job_id}/models/model.fbx"
                asset.fbx_url = fbx_url
                logger.info(f"FBX URL 생성: {fbx_url}")

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

@require_POST
@login_required
def publish_to_community(request, job_id):
    """
    메시 에셋을 커뮤니티에 바로 게시하는 API 뷰
    """
    try:
        # 디버깅을 위한 로깅 추가
        logger.info(f"게시 요청 받음: job_id={job_id}, 사용자={request.user.username}")
        
        # 요청된 에셋이 현재 사용자의 것인지 확인
        mesh_asset = get_object_or_404(MeshAsset, mesh_model__job_id=job_id, mesh_model__user=request.user)
        mesh_model = mesh_asset.mesh_model
        
        # 이미 게시된 적이 있는지 확인
        if Article.objects.filter(job=mesh_model).exists():
            logger.warning(f"이미 게시된 모델: job_id={job_id}")
            return JsonResponse({
                "success": False,
                "message": "이미 게시된 모델입니다."
            }, status=400)
        
        # 프롬프트 전체를 제목으로 사용 (제한하지 않음)
        title = mesh_model.create_prompt if mesh_model.create_prompt else f"Mesh {mesh_model.job_id[:8]}"
        
        # 새 게시글 생성 - 최소한의 정보만 포함
        article = Article(
            user_id=request.user,
            title=title,
            job=mesh_model,
            model_prompt=mesh_model.create_prompt or '',
            texture_prompt='',
            tags='3D, model',  # 기본 태그
            image=''  # 임시로 빈 값 설정 (save 메서드에서 채워짐)
        )
        
        # 게시글 저장 (save 메서드에서 model_seed 자동 생성)
        article.save()
        logger.info(f"게시글 생성 성공: id={article.id}, title={title}")
        
        # 성공 응답
        return JsonResponse({
            "success": True,
            "article_id": article.id,
            "message": "모델이 커뮤니티에 성공적으로 게시되었습니다."
        })
        
    except Exception as e:
        logger.error(f"Error publishing to community: {e}", exc_info=True)
        return JsonResponse({
            "success": False,
            "message": f"게시 중 오류가 발생했습니다: {str(e)}"
        }, status=500)


