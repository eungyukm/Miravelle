from django.shortcuts import render, get_object_or_404 , redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin # 로그인한 사용자만 특정 view에 접근할 수 있음
from .models import Article, Like
from django.http import HttpResponseForbidden # error 403(서버에 요청은 갔지만, 권한 때문에 요청 거절)
from .forms import ArticleForm
from django.db import DatabaseError

from workspace.models import MeshModel


# 게시글 목록 보기
class ArticleList(View):
    def get(self, request):
        try:
            article_list = Article.objects.all()
            model_list = MeshModel.objects.all()
            print(model_list.count())

            if not article_list.exists():
                article_list = None

        except DatabaseError as db_err:
            print(f"Database error occurred: {db_err}")
            article_list = None  # 데이터베이스 오류 시 None 설정

        except Exception as e:
            print(f"Unexpected error occurred: {e}")
            article_list = None  # 기타 예외 발생 시 None 설정

        context = {"article_list": article_list}
        return render(request, "main.html", context)
    
# 좋아요 게시물
class ArticleLike(LoginRequiredMixin, View): # 로그인 필수 기능 추가
    login_url = "/users/login/" # 로그인 되지 않았으면 로그인 url로 보냄
    
    def post(self, request,id, like_type): # 이렇게 적으면 article_id를 URL에서 받음
        article = get_object_or_404(Article, pk=id)
        user = request.user # 현재 로그인한 유저
        
        # like_type 유효성 검사 (모델 choices 사용)
        valid_like_types = [choice[0] for choice in Like.like_type.field.choices] #Like 모델 필드 LikeType의 choices 속성 사용
        if like_type not in valid_like_types:
            return HttpResponseForbidden("잘못된 요청입니다.")

        # 이미 좋아요/싫어요를 누른 경우 (예 : 취소 또는 변경)
        try:
            existing_like = Like.objects.get(user=user, article=article)
            if existing_like.like_type == like_type:
                # 같은 종류의 좋아요/싫어요를 다시 누른 경우 (예: 취소)
                existing_like.delete()
                
                if like_type == "❤️":
                    article.like_count = max(0, article.like_count - 1) # 최댓값 == 0, 게시물의 좋아요 개수에서 -1
                else:
                    article.dislike_count = max(0, article.dislike_count - 1) # 최댓값 == 0, like가 아니라 dislike일 경우
            else: # 예) 좋아요 -> 싫어요, 싫어요 -> 좋아요
                # 다른 종류의 좋아요/싫어요로 변경
                if like_type == "❤️":
                    article.like_count += 1
                    article.dislike_count = max(0, article.dislike_count - 1) # 싫어요 -> 좋아요로 간 경우임
                else:
                    article.like_count = max(0, article.like_count - 1)
                    article.dislike_count += 1
                existing_like.like_type = like_type
                existing_like.save() # 좋아요 또는 싫어요 관련 정보 저장.
            
            article.save() # 해당 게시물 저장
            
            
        except Like.DoesNotExist:
            # 좋아요/싫어요를 처음 누른 경우
            Like.objects.create(user=user, article=article, like_type=like_type)
            if like_type == "❤️":
                article.like_count += 1
            else:
                article.dislike_count += 1
            article.save()
            
        # HTTP_REFERER -> 이전 페이지 URL 포함하는 HTTP 헤더를 의미
        # request.META.get('HTTP_REFERER'): 현재 요청이 어느 페이지에서 왔는지 확인하는 것 (아까 request.get_full_path() 썼던 것과 같음)
        referer = request.META.get('HTTP_REFERER')
        # referer가 존재하면 (즉, 이전 페이지가 있으면)
        if referer:
            # 예: 상세 페이지에서 왔으면 상세 페이지로 메인에서 왔으면 메인으로 이동
            return redirect(referer)
        # referer가 없는 경우 메인 페이지로 리다이렉트(외부에서 들어왔을 시)
        return redirect("articles:main")
    
    
# 게시물 작성하기
class ArticleCreate(LoginRequiredMixin, View): # 로그인된 사용자만 접근 가능
    login_url = "/users/login/" # 로그인 안 돼 있으면 보내버림
    
    def get(self, request):
        form = ArticleForm()
        content = {"form":form}
        return render(request,"create.html", content)
    
    def post(self, request):
        form = ArticleForm(request.POST, request.FILES)
        print("폼 데이터:", request.POST) # 디버깅을 위해 폼 데이터 출력
        
        if form.is_valid():
            print("폼이 유효합니다.")
            article = form.save(commit=False)  # 즉시 저장하지 않고 Article 객체 생성
            article.user_id = request.user  # 현재 로그인한 사용자 설정
            article.save()  # 변경 사항과 함께 저장
            return redirect("articles:articledetail", article.pk)
        
        else:
            print("폼이 유효하지 않습니다. 오류:", form.errors) # 폼 오류 출력
            context = {"form": form}
            return render(request, "create.html", context)


# 게시물 상세보기
class ArticleDetail(LoginRequiredMixin, View):
    login_url = "/users/login/"

    def get(self, request, id):
        article = get_object_or_404(Article, pk=id)
        content = {
            "article": article
        }
        return render(request, "detail.html", content)
        