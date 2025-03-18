import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import MeshPromptModel

# utils
from workspace.meshy_utils import call_meshy_api  # Meshy API 호출 함수
from .serializers import GenerateMeshRequestSerializer  # Serializer 임포트

# 로깅 설정
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class GenerateMesh(APIView):
    """Mesh 생성 요청 & job_id 반환"""
    permission_classes = [IsAuthenticated]  # 로그인된 사용자만 접근 가능

    def get(self, request):
        """최근 생성된 Mesh 모델 목록 조회"""
        meshes = MeshPromptModel.objects.filter(user=request.user).order_by("-created_at")[:5]  # 최근 5개 조회
        results = [{"job_id": mesh.job_id, "status": mesh.status, "prompt": mesh.create_prompt, "art_style": mesh.art_style} for mesh in meshes]

        return Response({"recent_meshes": results}, status=status.HTTP_200_OK)
    
    def post(self, request):
        serializer = GenerateMeshRequestSerializer(data=request.data)
        if serializer.is_valid():
            prompt = serializer.validated_data['prompt']
            art_style = serializer.validated_data.get('art_style', 'realistic')

            # 프롬프트 보강: 중복 확인 후 "4K, highly detailed" 추가
            if "4K" not in prompt and "highly detailed" not in prompt:
                enhanced_prompt = prompt + ", 4K, highly detailed"
            else:
                enhanced_prompt = prompt  # 이미 포함된 경우 그대로 사용

            response_data = call_meshy_api("/openapi/v2/text-to-3d", "POST", {
                "mode": "preview", "prompt": enhanced_prompt, "art_style": art_style
            })

            if not response_data:
                return Response({"error": "Meshy API 응답 없음"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            job_id = response_data.get("result")
            if not job_id:
                return Response({"error": "Meshy API에서 job_id를 받지 못했습니다."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            MeshPromptModel.objects.create(
                user=request.user,
                job_id=job_id,
                status="processing",
                create_prompt=enhanced_prompt,  # 보강된 프롬프트 정보 저장
                art_style=art_style
            )

            return Response({"job_id": job_id, "message": "Mesh 생성 시작!"}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)