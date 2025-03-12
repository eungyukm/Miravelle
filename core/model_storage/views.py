from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.http import JsonResponse
from workspace.models import MeshModel
from articles.models import Article
import random

def first_publish(request):
    mesh = MeshModel.objects.first()
    if not mesh:
        return HttpResponse("MeshModel이 존재하지 않습니다.", status=404)

    article = Article.objects.create(
        user_id=mesh.user,
        job=mesh,
        title=f"New Mesh: {mesh.job_id}",
        model_prompt=mesh.create_prompt,
        texture_prompt="Generated Texture",
        model_seed=generate_unique_model_seed(),
        image=mesh.image_path,
        tags="mesh, 3D"
    )

    return HttpResponse(f"첫 번째 게시글이 성공적으로 공개되었습니다. (Article ID: {article.id})")

def publish_article(request, id):
    if request.method == 'POST':
        print(f"publish_article id {id}")
        # UUID로 검색
        mesh = get_object_or_404(MeshModel, job_id=id)

        article = Article.objects.create(
            user_id=mesh.user,
            job=mesh,
            title=f"New Mesh: {mesh.job_id}",
            model_prompt=mesh.create_prompt,
            texture_prompt="Generated Texture",
            model_seed=generate_unique_model_seed(),
            image=mesh.image_path,
            tags="mesh, 3D"
        )

        return JsonResponse({
            'status': 'success',
            'article_id': article.id,
            'message': 'Article successfully published'
        })

    return JsonResponse({'status': 'error', 'error': 'Invalid request'}, status=400)

def generate_unique_model_seed():
    while True:
        seed = random.randint(1, 2147483648)
        if not Article.objects.filter(model_seed=seed).exists():
            return seed
