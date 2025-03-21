# prompts/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from openai import AsyncOpenAI
import asyncio
import os
import openai
from drf_yasg.utils import swagger_auto_schema 
from .serializers import GeneratePromptSerializer

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("Missing OpenAI API Key")

aclient = AsyncOpenAI(api_key=api_key)


# OpenAI 프롬프트 생성 함수
async def generate_3d_prompt(user_input):
    system_prompt = (
        "너는 3D 모델을 생성하기 위한 최적의 프롬프트를 만드는 AI야. "
        "사용자의 요청을 분석하여 디테일한 프롬프트를 제공해야 해. "
        "프롬프트는 구체적인 특징(색상, 분위기, 배경, 스타일 등)을 포함해야 하며, "
        "모델링에 적합한 키워드 중심으로 작성해야 해."
        "개행문자는 제거해 줘."
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
class GeneratePromptAPI(APIView):
    
    def get(self, request):
        message = "API is running"
        return Response({"status": message}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=GeneratePromptSerializer,
        operation_description="3D 모델 생성을 위한 프롬프트 생성 API",
    )
    def post(self, request):
        serializer = GeneratePromptSerializer(data=request.data)
        if serializer.is_valid():
            user_input = serializer.validated_data['user_input']
            # OpenAI API 호출을 위한 사용자 입력
            user_request = "Create a 3D model based on 3D Model Prompt: {}".format(user_input)

            # OpenAI API 호출을 비동기적으로 실행하고 결과를 얻음
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            optimized_prompt = loop.run_until_complete(generate_3d_prompt(user_request))
            loop.close()

            # JSON 형태로 응답 반환
            return Response({"Miravelle": optimized_prompt}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)