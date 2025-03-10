from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils import timezone
from datetime import timedelta
from workspace.models import MeshModel
from .models import Asset, MeshAsset
import requests

# Create your views here.

class AssetListView(LoginRequiredMixin, ListView):
    """
    사용자의 3D 모델 에셋 목록을 보여주는 뷰
    - MeshModel에서 생성된 에셋
    - 업로드된 에셋
    """
    model = Asset
    template_name = 'assets/asset_list.html'
    context_object_name = 'assets'
    
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
                }
            )
            
            # URL이 없거나 오래된 경우 업데이트 (1시간 기준)
            if not asset.thumbnail_url or (
                asset.last_url_update and 
                timezone.now() - asset.last_url_update > timedelta(hours=1)
            ):
                try:
                    asset.update_urls()
                except Exception as e:
                    print(f"Error updating URLs for {asset}: {e}")
            
            mesh_assets.append(asset)
        
        context['mesh_assets'] = mesh_assets
        return context
    
    def get_queryset(self):
        """현재 로그인한 사용자의 에셋만 필터링하여 반환"""
        return Asset.objects.filter(user=self.request.user).order_by('-created_at')


@require_POST
@login_required
def delete_asset(request, pk):
    """
    에셋을 삭제하는 뷰
    
    Args:
        request: HTTP 요청 객체
        pk: 삭제할 에셋의 primary key
    
    Returns:
        JsonResponse: 삭제 성공/실패 여부
    """
    try:
        # 에셋이 존재하는지, 그리고 현재 사용자의 것인지 확인
        asset = get_object_or_404(Asset, pk=pk, user=request.user)
        
        # 파일 삭제 시도 (나중에 Azure Storage 삭제 로직 추가 필요)
        try:
            if asset.thumbnail:
                asset.thumbnail.delete(save=False)  # 실제 파일만 삭제
        except Exception as e:
            print(f"썸네일 삭제 중 오류 발생: {e}")
            # 썸네일 삭제 실패는 무시하고 계속 진행
        
        # 에셋 삭제
        asset.delete()
        
        return JsonResponse({
            "message": "Asset deleted successfully",
            "asset_id": pk
        })
        
    except Asset.DoesNotExist:
        return JsonResponse({
            "error": "에셋을 찾을 수 없습니다."
        }, status=404)
    except Exception as e:
        print(f"에셋 삭제 중 오류 발생: {e}")  # 서버 로그에 에러 기록
        return JsonResponse({
            "error": f"삭제 중 오류가 발생했습니다: {str(e)}"
        }, status=500)

# ────────────────────────── 테스트용 에셋 생성 페이지 ──────────────────────────

@login_required
def create_asset(request):
    """
    에셋 생성 페이지를 보여주고 생성을 처리하는 뷰
    GET: 생성 폼 페이지 표시
    POST: 에셋 생성 처리
    """
    if request.method == 'POST':
        try:
            # Asset 생성
            asset = Asset.objects.create(
                user=request.user,
                title=request.POST.get('title'),
                content=request.POST.get('content', ''),
                file_path=request.POST.get('file_path', ''),
                thumbnail=request.FILES.get('thumbnail') if 'thumbnail' in request.FILES else None
            )
            return redirect('assets:asset_list')
            
        except Exception as e:
            return render(request, 'assets/asset_create.html', {
                'error': str(e)
            })
    
    return render(request, 'assets/asset_create.html')


# ────────────────────────── 테스트용 에셋 생성 API ──────────────────────────
@csrf_exempt
@login_required
def test_create_asset(request):
    """
    테스트용: 3D 모델을 My Assets에 추가하는 API
    POST 요청 예시:
    {
        "title": "Test 3D Model",
        "content": "This is a test model",
        "file_path": "test/path/model.fbx",
        "thumbnail_url": "http://example.com/thumbnail.jpg"  # 선택사항
    }
    """
    if request.method != "POST":
        return JsonResponse({"error": "POST request required"}, status=405)
    
    try:
        import json
        data = json.loads(request.body.decode('utf-8'))
        
        # Asset 생성
        asset = Asset.objects.create(
            user=request.user,
            title=data.get('title', 'Test 3D Model'),
            content=data.get('content', ''),
            file_path=data.get('file_path', ''),
            # thumbnail은 선택사항
            thumbnail=data.get('thumbnail_url') if data.get('thumbnail_url') else None
        )
        
        return JsonResponse({
            "message": "Asset created successfully",
            "asset_id": asset.id,
            "title": asset.title
        })
        
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
# ──────────────────────────── 여기 까지 테스트 코드 ────────────────────────────

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


