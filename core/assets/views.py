from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import Asset

# Create your views here.

class AssetListView(LoginRequiredMixin, ListView):
    """
    사용자의 3D 모델 에셋 목록을 보여주는 뷰
    """
    model = Asset  # 모델 지정
    template_name = 'assets/asset_list.html'  # 템플릿 지정
    context_object_name = 'assets'  # 컨텍스트 객체 이름 지정
    
    def get_queryset(self):
        """현재 로그인한 사용자의 에셋만 필터링하여 반환"""
        return Asset.objects.filter(user=self.request.user).order_by('-created_at')


class AssetDetailView(LoginRequiredMixin, DetailView):
    """
    3D 모델 에셋의 상세 정보를 보여주는 뷰
    """
    model = Asset
    template_name = 'assets/asset_detail.html'
    context_object_name = 'asset'
    
    def get_queryset(self):
        """현재 로그인한 사용자의 에셋만 필터링"""
        return Asset.objects.filter(user=self.request.user)


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
        asset = get_object_or_404(Asset, pk=pk, user=request.user)
        
        # 파일 삭제 (나중에 Azure Storage 삭제 로직 추가 필요)
        if asset.thumbnail:
            asset.thumbnail.delete()
        
        # 에셋 삭제
        asset.delete()
        
        return JsonResponse({"message": "Asset deleted successfully"})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


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


@login_required
def update_asset(request, pk):
    """
    에셋 수정 뷰
    GET: 수정 폼 표시
    POST: 수정 사항 저장
    """
    asset = get_object_or_404(Asset, pk=pk, user=request.user)
    
    if request.method == "POST":
        # POST 요청 처리
        asset.title = request.POST.get('title', asset.title)
        asset.content = request.POST.get('content', asset.content)
        asset.save()
        return redirect('assets:asset_detail', pk=asset.pk)
        
    # GET 요청 처리
    return render(request, 'assets/asset_edit.html', {'asset': asset})
