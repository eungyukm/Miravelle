import re
from django.shortcuts import render, get_object_or_404 , redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin # 로그인한 사용자만 특정 view에 접근할 수 있음
from .models import Article, Like
from django.http import HttpResponseForbidden # error 403(서버에 요청은 갔지만, 권한 때문에 요청 거절)
from .forms import ArticleForm
from django.db import DatabaseError
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage  # 250325 추가


def get_image_url(article):
    if article.image_path:
        if article.image_path.name.startswith('http'):
            return article.image_path.name
        return article.image_path.url
    return None


# 게시글 목록 보기
class ArticleList(View):
    def get(self, request):
        try:
            article_list = Article.objects.all().order_by("-id") # 250325 수정
        
            if not article_list.exists():
                article_list = None
            
            page = request.GET.get("page", 1) # URL에서 현재 페이지 번호를 가져옴 (기본값: 1) 250325 추가
            paginator = Paginator(article_list, 6) # 페이지당 6개의 게시물로 페이지네이터 생성 250325 추가
            
            try: # 예외 처리 추가
                articles = paginator.get_page(page)  # 요청된 페이지에 해당하는 게시물 가져오기 250325 추가
            except PageNotAnInteger: # 페이지 번호가 정수가 아닌 경우 250325 추가
                articles = paginator.get_page(1) # 1페이지를 보여준다 250325 추가
            except EmptyPage: # 페이지가 비어있는 경우 250325 추가
                articles = paginator.get_page(paginator.num_pages) # 마지막 페이지를 보여준다 250325 추가
        
            is_paginated = articles.has_other_pages()  # 페이지네이션이 필요한지 확인 250325 추가
            
            
        except DatabaseError as db_err:
            print(f"Database error occurred: {db_err}")
            article_list = None  # 데이터베이스 오류 시 None 설정

        except Exception as e:
            print(f"Unexpected error occurred: {e}")
            article_list = None  # 기타 예외 발생 시 None 설정

        context = {
            "article_list": article_list,
            "articles": articles,  # 현재 페이지의 게시물 250325 추가
            "is_paginated": is_paginated,  # 페이지네이션 UI를 표시할지 여부 250325 추가
            }
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

        # job_id 값 추출
        job_string = str(article.job) if article.job else ""   # 문자열로 변환
        job_match = re.search(r'[0-9a-fA-F-]{36}', job_string)
        job_id = job_match.group(0) if job_match else None

        # 서버 측 로그 출력
        print(f"[LOG] Article ID: {id}")
        print(f"[LOG] Extracted job_id: {job_id}")

        content = {
            "article": article,
            "job_id": job_id,  # job_id 값만 템플릿에 전달
        }
        return render(request, "detail.html", content)
