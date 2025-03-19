# prompts/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from openai import AsyncOpenAI
import asyncio
import os


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
    )

    response = await aclient.chat.completions.create(model="gpt-4o",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_input}
    ])

    return response.choices[0].message.content

# Django REST Framework API 엔드포인트
class GeneratePromptAPI(APIView):
    def post(self, request):
        user_request = request.data.get("user_input", "")

        if not user_request:
            return Response({"error": "user_input is required"}, status=status.HTTP_400_BAD_REQUEST)

        # OpenAI API 호출을 비동기적으로 실행하고 결과를 얻음
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        optimized_prompt = loop.run_until_complete(generate_3d_prompt(user_request))
        loop.close()

        return Response({"generated_prompt": optimized_prompt}, status=status.HTTP_200_OK)
