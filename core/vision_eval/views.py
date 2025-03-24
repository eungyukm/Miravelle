from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def get_image_url(request):
    data = {
        'url': 'https://example.com'
    }
    return Response(data)
