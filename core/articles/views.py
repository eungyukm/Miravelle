from django.shortcuts import render

# 게시글 목록 보기
def ArticleList(request):
    return render(request, "main.html")