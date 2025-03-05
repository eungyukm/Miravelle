from django.shortcuts import render, get_object_or_404 , redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin # 로그인한 사용자만 특정 view에 접근할 수 있음
from .models import Article, Like
from django.http import HttpResponseForbidden # error 403(서버에 요청은 갔지만, 권한 때문에 요청 거절)
from .forms import ArticleForm

# 게시글 목록 보기
class ArticleList(View):
    def get(self, request):
        article_list = Article.objects.all()
        context = {"article_list":article_list}
        return render(request, "main.html", context)
    
# 좋아요 게시물
class ArticleLike(LoginRequiredMixin, View): # 로그인 필수 기능 추가
    login_url = "/users/login/" # 로그인 되지 않았으면 로그인 url로 보냄
    
    def post(self, request, pk, like_type): # 이렇게 적으면 article_id를 URL에서 받음
        article = get_object_or_404(Article, pk=pk)
        user = request.user # 현재 로그인한 유저
        
        # 오류 처리
        if like_type not in [("Like","like"), ("Dislike", "dislike")]:
            return HttpResponseForbidden("잘못된 요청입니다.")
        
        # 이미 좋아요/싫어요를 누른 경우 (예 : 취소 또는 변경)
        try:
            existing_like = Like.objects.get(user=user, article=article)
            if existing_like.like_type == like_type:
                # 같은 종류의 좋아요/싫어요를 다시 누른 경우 (예: 취소)
                existing_like.delete()
                
                if like_type == "like":
                    article.like_count = max(0, article.like_count - 1) # 최댓값 == 0, 게시물의 좋아요 개수에서 -1
                else:
                    article.dislike_count = max(0, article.dislike_count - 1) # 최댓값 == 0, like가 아니라 dislike일 경우
            else: # 예) 좋아요 -> 싫어요, 싫어요 -> 좋아요
                # 다른 종류의 좋아요/싫어요로 변경
                if like_type == "like":
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
            if like_type == "like":
                article.like_count += 1
            else:
                article.dislike_count += 1
            article.save()
        return redirect("ArticleDetail", pk=pk) # 상세 페이지로 리다이렉션
    
    
# 게시물 작성하기
class ArticleCreate(LoginRequiredMixin, View): # 로그인된 사용자만 접근 가능
    login_url = "/users/login/" # 로그인 안 돼 있으면 보내버림
    
    def post(self, request):
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save()
            return redirect("articles:articledetail", article.pk)


# 게시물 상세보기
class ArticleDetail(LoginRequiredMixin, View):
    login_url = "/users/login/"
    
    def get(self, request, pk):
        article = get_object_or_404(Article, pk=pk)
        form = ArticleForm(article)
        content = {
            "form":form
            }
        return render(request, "detail.html", content)
        