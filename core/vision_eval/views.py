from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from articles.models import Article
from articles.serializers import ArticleSerializer
from .serializers import EvaluationSerializer
from .models import Evaluation

@api_view(['GET'])
def get_image_url(request):
    data = {
        'url': 'https://example.com'
    }
    return Response(data)

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
