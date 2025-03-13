import requests
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from utils.azure_key_manager import AzureKeyManager

class MeshyTextTo3DView(APIView):
    def get(self, request, task_id):

        azure_keys = AzureKeyManager.get_instance()
        print(azure_keys.connection_string)
        url = f"https://api.meshy.ai/openapi/v2/text-to-3d/{task_id}"
        headers = {
            "Authorization": f"Bearer {azure_keys.meshy_api_key}"
        }
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return Response(response.json(), status=status.HTTP_200_OK)
        except requests.exceptions.RequestException as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)