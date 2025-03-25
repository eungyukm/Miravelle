from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
import asyncio
import os
import json
import sys
import logging
from openai import AsyncOpenAI
from prompts.serializers import (
    EnhancedPromptInputSerializer,
    EnhancedPromptSerializer
)
from .models import EnhancedPrompt
import openai
from drf_yasg.utils import swagger_auto_schema 
from prompts.serializers import GeneratePromptSerializer
from django.utils.decorators import method_decorator # 250324 추가
from django.contrib.auth.decorators import login_required # 250324 추가
from django.http import JsonResponse # 250324 추가
from django.shortcuts import render # 250325 추가


from utils.azure_key_manager import AzureKeyManager

# 로깅 설정
logger = logging.getLogger(__name__)

# 에이전트 임포트 경로 설정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

# API 키 직접 설정
azure_keys = AzureKeyManager.get_instance()
api_key = azure_keys.openai_api_key
if not api_key:
    raise ValueError("Missing OpenAI API Key")

# 에이전트 임포트
try:
    from agents.prompt_enhancer.api import prompt_enhancer_api
    AGENT_ENABLED = True
    logger.info("Successfully imported prompt_enhancer_api")
except ImportError as e:
    AGENT_ENABLED = False
    logger.error(f"Error importing prompt_enhancer_api: {str(e)}")
    print(f"Warning: Prompt enhancer agent could not be imported: {str(e)}")

# 전역 OpenAI 클라이언트 설정
aclient = AsyncOpenAI(api_key=api_key)

# OpenAI 프롬프트 생성 함수
async def generate_3d_prompt(user_input):
    # 전역 클라이언트 사용
    system_prompt = (
        "너는 3D 모델을 생성하기 위한 최적의 프롬프트를 만드는 AI야."
        "사용자의 요청을 분석하여 디테일한 프롬프트를 제공해야 해."
        "사용자가 제공한 정보를 존중하며, 부족한 경우 일반적인 추천을 추가해."
        "3D 모델링에 적합한 키워드를 선정하고, 문장은 직관적이며 이해하기 쉽게 작성해."
        "프롬프트 내의 개행을 삭제하고, 자연스럽게 이어지도록 구성해."
        "필요한 정보를 압축해 500자 이내로 한국어로 작성해."
    )

    try:
        response = await aclient.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ]
        )
        return response.choices[0].message.content
    except openai.APIConnectionError as e:
        print(f"OpenAI 서버 연결 오류: {e}")
        return "OpenAI 서버 연결에 실패했습니다. 잠시 후 다시 시도해주세요."
    except openai.RateLimitError as e:
        print(f"OpenAI API Rate Limit 초과: {e}")
        return "OpenAI API Rate Limit이 초과되었습니다. 잠시 후 다시 시도해주세요."
    except Exception as e:
        print(f"OpenAI API 호출 중 오류 발생: {e}")
        return "OpenAI API 호출 중 오류가 발생했습니다."


# Django REST Framework API 엔드포인트
@method_decorator(login_required(login_url='users:login'), name='dispatch')
class GeneratePromptAPI(APIView):
    
    def get(self, request):
        # 250325 : API 상태 확인 대신 prompt.html 렌더링
        print(self.__class__.__name__ + "request: ", request) # request가 찍히는지 확인 250325
        return render(request, "prompt.html")
        # message = "API가 사용 가능한 상태입니다."
        # return JsonResponse({"status": message}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=GeneratePromptSerializer,
        operation_description="3D 모델 생성을 위한 프롬프트 생성 API",
    )
    def post(self, request):
        serializer = GeneratePromptSerializer(data=request.data)
        if serializer.is_valid():
            user_input = serializer.validated_data['user_input']
            user_request = "Create a 3D model based on 3D Model Prompt: {}".format(user_input)

            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                optimized_prompt = loop.run_until_complete(generate_3d_prompt(user_request))
                loop.close()
                print("optimized_prompt: ", optimized_prompt) # optimized_prompt가 출력되는지 확인 250325
                
                return JsonResponse({"Miravelle": optimized_prompt}, status=status.HTTP_200_OK)   # 20250324
            except Exception as e:
                return JsonResponse(
                    {"error": f"API 호출 중 오류 발생: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        else:
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EnhancePromptAPI(APIView):
    """
    랭체인 에이전트를 사용하여 3D 모델 생성 프롬프트를 개선하는 API 뷰입니다.
    """
    # 인증 필요 없이 누구나 접근 가능하도록 설정
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="프롬프트 개선 에이전트 상태 확인",
        responses={200: "API 활성화 상태"}
    )
    def get(self, request):
        return Response({
            "status": "active" if AGENT_ENABLED else "disabled",
            "message": "Prompt enhancement agent is ready" if AGENT_ENABLED else "Prompt enhancement agent is not available"
        }, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        request_body=EnhancedPromptInputSerializer,
        operation_description="3D 모델 생성을 위한 프롬프트 개선 API",
        responses={200: EnhancedPromptSerializer}
    )
    def post(self, request):
        """
        사용자가 입력한 프롬프트를 개선하여 더 좋은 프롬프트를 생성합니다.
        """
        serializer = EnhancedPromptInputSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        if not AGENT_ENABLED:
            return Response(
                {"error": "Prompt enhancement agent is not available"}, 
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        try:
            # 사용자 입력 프롬프트 가져오기
            original_prompt = serializer.validated_data['prompt']
            user_id = serializer.validated_data.get('user_id')
            
            # 에이전트를 사용하여 프롬프트 개선
            result = prompt_enhancer_api.process_and_save(original_prompt)
            
            # 데이터베이스 저장 후 ID가 없으면 직접 저장
            if not result.get('db_id'):
                from django.contrib.auth import get_user_model
                User = get_user_model()
                
                # 사용자 정보 가져오기
                user = None
                if user_id:
                    try:
                        user = User.objects.get(id=user_id)
                    except User.DoesNotExist:
                        pass
                
                # 모델 직접 저장
                enhanced_prompt = EnhancedPrompt.objects.create(
                    user=user,
                    original_prompt=result['original_prompt'],
                    enhanced_prompts=json.dumps(result['enhanced_prompts']),
                    selected_prompt=result['selected_prompt'],
                    selection_reason=result.get('selection_reason', ''),
                    scores=json.dumps(result.get('scores', {}))
                )
                
                result['db_id'] = enhanced_prompt.id
            
            # EnhancedPrompt 객체 가져오기
            enhanced_prompt = EnhancedPrompt.objects.get(id=result['db_id'])
            
            # 시리얼라이저를 사용하여 응답 데이터 생성
            response_serializer = EnhancedPromptSerializer(enhanced_prompt)
            
            return Response(response_serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response(
                {"error": f"Error processing prompt: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

