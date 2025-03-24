from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from django.db import transaction
from articles.models import Article
from articles.serializers import ArticleSerializer
from .serializers import EvaluationSerializer
from .models import Evaluation

@api_view(['GET'])
def get_evaluation_image(request):
    try:
        # 평가되지 않은 이미지 찾기 (Evaluation 모델에 없는 경우)
        article = Article.objects.exclude(
            id__in=Evaluation.objects.values_list('article_id', flat=True)
        ).first()
        
        if not article:
            return Response({"message": "No images available for evaluation."}, status=status.HTTP_404_NOT_FOUND)
        
        # 반환할 데이터 생성
        serializer = ArticleSerializer(article)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def save_evaluation(request, pk):
    print(f"Received pk: {pk}")
    try:
        article = Article.objects.get(pk=pk)

        # 이미 평가된 경우 중복 처리 방지
        if Evaluation.objects.filter(article=article).exists():
            return Response({"message": "This image has already been evaluated."}, status=status.HTTP_400_BAD_REQUEST)

        # 트랜잭션으로 평가 저장
        with transaction.atomic():
            evaluation = Evaluation.objects.create(
                article=article,
                evaluation_score=request.data.get('evaluation_score'),
            )
            evaluation.save()

        return Response({"message": "Evaluation saved successfully."}, status=status.HTTP_201_CREATED)

    except Article.DoesNotExist:
        return Response({"error": "Article not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)