from rest_framework.views import APIView
# from rest_framework.response import Response
from rest_framework import status
from openai import AsyncOpenAI
import asyncio
import openai
from drf_yasg.utils import swagger_auto_schema 
from prompts.serializers import GeneratePromptSerializer
from django.utils.decorators import method_decorator # 250324 추가
from django.contrib.auth.decorators import login_required # 250324 추가
from django.http import JsonResponse # 250324 추가
from django.shortcuts import render # 250325 추가


from utils.azure_key_manager import AzureKeyManager

# OpenAI 프롬프트 생성 함수
async def generate_3d_prompt(user_input):
    azure_keys = AzureKeyManager.get_instance()
    api_key = azure_keys.openai_api_key
    
    if not api_key:
        raise ValueError("Missing OpenAI API Key")

    aclient = AsyncOpenAI(api_key=api_key)
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