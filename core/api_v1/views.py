import requests
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.decorators import api_view
from utils.azure_key_manager import AzureKeyManager

class Generate3DPreview(APIView):
    @swagger_auto_schema(
        operation_id="generate_3d_preview",
        manual_parameters=[
            openapi.Parameter('task_id', openapi.IN_PATH, description="Task ID", type=openapi.TYPE_STRING)
        ],
        responses={200: "3D preview generated"}
    )
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

class Refine3DPreview(APIView):
    @swagger_auto_schema(
        operation_description="Generate 3D model using Meshy AI",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'mode': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Generation mode (e.g., refine)',
                    default="refine"
                ),
                'preview_task_id': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Preview task ID'
                ),
                'enable_pbr': openapi.Schema(
                    type=openapi.TYPE_BOOLEAN, 
                    description='Enable PBR (Physically Based Rendering)',
                    default=True
                )
            },
            required=['mode', 'preview_task_id', 'enable_pbr'],
        ),
        responses={
            200: openapi.Response(
                description="3D model generation successful",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'result': openapi.Schema(type=openapi.TYPE_STRING, description='Result status'),
                        '3d_model_url': openapi.Schema(type=openapi.TYPE_STRING, description='URL of the generated 3D model')
                    }
                )
            ),
            400: "Bad request",
            500: "Server error"
        }
    )
    def post(self, request):
        mode = request.data.get('mode')
        preview_task_id = request.data.get('preview_task_id')
        enable_pbr = request.data.get('enable_pbr')

        if not mode or not preview_task_id:
            return Response({"error": "Missing required parameters"}, status=status.HTTP_400_BAD_REQUEST)
        

        azure_keys = AzureKeyManager.get_instance()
        headers = {
            "Authorization": f"Bearer {azure_keys.meshy_api_key}"
        }

        payload = {
            "mode": mode,
            "preview_task_id": preview_task_id,
            "enable_pbr": enable_pbr
        }

        try:
            response = requests.post(
                "https://api.meshy.ai/openapi/v2/text-to-3d",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            return Response(response.json(), status=response.status_code)
        except requests.exceptions.RequestException as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class List3DModelsView(APIView):
    @swagger_auto_schema(
        operation_description="List generated 3D models",
        manual_parameters=[
            openapi.Parameter(
                'page_size',
                openapi.IN_QUERY,
                description="Number of results per page",
                type=openapi.TYPE_INTEGER
            )
        ],
        responses={
            200: openapi.Response(
                description="List of 3D models",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'results': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            description='List of models',
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'id': openapi.Schema(type=openapi.TYPE_STRING, description='Model ID'),
                                    'name': openapi.Schema(type=openapi.TYPE_STRING, description='Model name'),
                                    'url': openapi.Schema(type=openapi.TYPE_STRING, description='Model URL'),
                                }
                            )
                        ),
                        'next': openapi.Schema(type=openapi.TYPE_STRING, description='Next page URL'),
                        'previous': openapi.Schema(type=openapi.TYPE_STRING, description='Previous page URL'),
                        'count': openapi.Schema(type=openapi.TYPE_INTEGER, description='Total number of models'),
                    }
                )
            ),
            400: "Bad request",
            500: "Server error"
        }
    )
    def get(self, request):
        page_size = request.query_params.get('page_size', 10)
        azure_keys = AzureKeyManager.get_instance()

        headers = {
            "Authorization": f"Bearer {azure_keys.meshy_api_key}"
        }

        params = {
            "page_size": page_size
        }

        try:
            response = requests.get(
                "https://api.meshy.ai/openapi/v2/text-to-3d",
                headers=headers,
                params=params
            )
            response.raise_for_status()
            return Response(response.json(), status=response.status_code)
        except requests.exceptions.RequestException as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)