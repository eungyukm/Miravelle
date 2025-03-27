from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.db import DatabaseError
from django.views import View
from utils.azure_key_manager import AzureKeyManager
from workspace.models import MeshModel
from .models import MeshAsset
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s") 
logger = logging.getLogger(__name__) 

# AzureKeyManager 인스턴스 가져오기
azure_keys = AzureKeyManager.get_instance()

class AssetListView(LoginRequiredMixin, View):
    """
    사용자의 3D 모델 에셋 목록을 보여주는 뷰
    - MeshModel에서 생성된 에셋만 표시
    """
    login_url = "/users/login/" # 로그인 되지 않았으면 로그인 url로 보냄
    
    def get(self, request):
        try:
            # 사용자의 MeshModel에 해당하는 MeshAsset 가져오기
            mesh_models = MeshModel.objects.filter(user=request.user).order_by('-created_at')
            mesh_assets = []
            
            for mesh_model in mesh_models:
                # MeshAsset이 없으면 생성
                asset, created = MeshAsset.objects.get_or_create(
                    mesh_model=mesh_model,
                    defaults={
                        'title': f'Mesh {mesh_model.job_id[:8]}',
                        'prompt': mesh_model.create_prompt,
                    }
                )
                
                # URL 업데이트
                try:
                    job_id = mesh_model.job_id # 작업 ID
                    storage_account_name = azure_keys.storage_account_name or "miravelledevstorage" # 스토리지 계정 이름
                    container_name = azure_keys.container_name or "meshy-3d-assets" # 컨테이너 이름
                    
                    # 썸네일 URL 생성
                    thumbnail_url = f"https://{storage_account_name}.blob.core.windows.net/{container_name}/tasks/{job_id}/previews/preview.png"
                    asset.thumbnail_url = thumbnail_url
                    
                    # FBX URL 생성
                    fbx_url = f"https://{storage_account_name}.blob.core.windows.net/{container_name}/tasks/{job_id}/models/model.fbx"
                    asset.fbx_url = fbx_url
                    
                    # 텍스처 URL 생성 (base_color_path)
                    # 텍스처가 없을 수 있으므로 base_color_path가 없는 경우를 처리
                    if mesh_model.base_color_path:
                        texture_url = f"https://{storage_account_name}.blob.core.windows.net/{container_name}/tasks/{job_id}/textures/base_color.png"
                        asset.texture_url = texture_url
                        asset.has_texture = True
                    else:
                        asset.texture_url = ""
                        asset.has_texture = False
                    
                    asset.save()
                except Exception as e:
                    logger.error(f"Error updating URLs for {asset}: {e}") # 썸네일과 FBX URL 업데이트 오류 로깅
                
                mesh_assets.append(asset)
            
            if not mesh_assets:
                mesh_assets = None
            
            page = request.GET.get("page", 1) # 페이지 번호 가져오기
            paginator = Paginator(mesh_assets, 6) # 페이지당 6개의 에셋으로 페이지네이터 생성
            
            try:
                assets = paginator.get_page(page)
            except PageNotAnInteger: # 페이지 번호가 정수가 아닌 경우
                assets = paginator.get_page(1)
            except EmptyPage: # 페이지가 비어있는 경우
                assets = paginator.get_page(paginator.num_pages) # 마지막 페이지로 이동
            
            is_paginated = assets.has_other_pages() # 페이지네이션이 필요한지 확인
            
        except DatabaseError as db_err: # 데이터베이스 오류 발생 시
            logger.error(f"Database error occurred: {db_err}")
            assets = []
            is_paginated = False
        except Exception as e: # 기타 예외 발생 시
            logger.error(f"Unexpected error occurred: {e}")
            assets = []
            is_paginated = False

        context = {
            "assets": assets, # 페이지네이션 적용된 에셋 목록
            "is_paginated": is_paginated, # 페이지네이션 사용 여부
        }
        return render(request, "assets/asset_list.html", context)

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
def publish_to_community(request, asset_id):
    """
    메시 에셋을 커뮤니티에 게시하는 뷰
    """
    try:
        from articles.models import Article
        import random
        
        # 사용자 소유의 에셋인지 확인
        mesh_asset = get_object_or_404(MeshAsset, id=asset_id, mesh_model__user=request.user)
        mesh_model = mesh_asset.mesh_model
        
        # 이미 게시된 에셋인지 확인
        existing_article = Article.objects.filter(job=mesh_model).first()
        if existing_article:
            logger.info(f"Asset {asset_id} is already published as article {existing_article.id}")
            return JsonResponse({
                "success": True,
                "message": "이미 커뮤니티에 게시되었습니다.",
                "article_id": existing_article.id
            })
        
        # 에셋 정보 가져오기
        title = mesh_asset.title or f'Mesh {mesh_model.job_id[:8]}'
        prompt = mesh_asset.prompt or mesh_model.create_prompt
        
        # 아티클 생성
        article = Article(
            user_id=request.user,
            title=f"3D 모델 공유: {title}",
            model_prompt=prompt,
            texture_prompt="",  # 텍스처 프롬프트 정보가 없는 경우 빈 문자열 설정
            tags="3D,Model,Mesh",
            job=mesh_model
        )
        
        # model_seed는 자동 생성됨 (Article.save에서 처리)
        article.save()  # save 메서드에서 job의 여러 필드들이 복사됨
        
        logger.info(f"Asset {asset_id} published to community as article {article.id}")
        
        return JsonResponse({
            "success": True,
            "message": "성공적으로 커뮤니티에 게시되었습니다!",
            "article_id": article.id
        })
        
    except ImportError as ie:
        logger.error(f"Articles app is not installed or properly configured: {ie}")
        return JsonResponse({
            "success": False,
            "error": "Articles 앱이 설치되지 않았습니다."
        }, status=500)
    except Exception as e:
        logger.error(f"Error publishing asset {asset_id} to community: {e}")
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=500)



