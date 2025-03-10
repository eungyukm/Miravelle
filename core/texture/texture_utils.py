import requests  # HTTP 요청을 보내기 위한 라이브러리
from core.env import MESHY_API_KEY


# API 요청에 전달할 데이터 (페이로드)
payload = {
    "model_url": "https://cdn.meshy.ai/model/example_model_2.glb",  
    # 텍스처를 적용할 3D 모델의 URL (GLB 파일)

    "object_prompt": "a monster mask",  
    # 3D 모델이 어떤 오브젝트인지 설명하는 프롬프트 (ex: 괴물 가면)

    "style_prompt": "red fangs, Samurai outfit that fused with japanese batik style",  
    # 적용할 텍스처 스타일에 대한 설명 (빨간 송곳니, 사무라이 의상, 일본 바틱 스타일)

    "enable_original_uv": True,  
    # 원본 UV 매핑을 유지할지 여부 (True면 원본 UV 맵을 유지)

    "enable_pbr": True,  
    # PBR (Physically Based Rendering) 기반 텍스처 적용 여부 (True면 PBR 적용)

    "resolution": "1024",  
    # 생성할 텍스처의 해상도 (픽셀 단위, 1024x1024)

    "negative_prompt": "low quality, low resolution, low poly, ugly",  
    # 원하지 않는 스타일을 제외하기 위한 네거티브 프롬프트 (저품질, 저해상도, 저폴리, 못생김 배제)

    "art_style": "realistic"  
    # 생성할 텍스처의 스타일 (ex: realistic → 사실적인 스타일)
}

# API 요청을 위한 헤더 설정
headers = {
    "Authorization": f"Bearer {MESHY_API_KEY}"  
    # 인증을 위한 Bearer 토큰 (YOUR_API_KEY 부분을 실제 API 키로 변경해야 함)
}

# Meshy API의 text-to-texture 엔드포인트에 POST 요청을 보냄
response = requests.post(
    "https://api.meshy.ai/openapi/v1/text-to-texture",  # API 엔드포인트
    headers=headers,  # 인증 헤더 포함
    json=payload,  # JSON 형식의 데이터 전송
)

# 요청이 실패하면 예외 발생 (에러 처리)
response.raise_for_status()

# API 응답 출력 (JSON 데이터 형태로 출력됨)
print(response.json())

