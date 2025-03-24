"""
프롬프트 엔핸서 에이전트의 설정 파일입니다.
"""

# 기본 설정
DEFAULT_MODEL_NAME = "gpt-4o"  # 기본 모델
DEFAULT_TEMPERATURE = 0.7      # 창의성 조절 (0.0-1.0)
DEFAULT_MAX_TOKENS = 2048      # 최대 토큰 수
DEFAULT_NUM_SUGGESTIONS = 5    # 생성할 프롬프트 제안 수
DEFAULT_BASE_PROMPT_IMPROVEMENT_INSTRUCTIONS = """
다음 항목을 개선하세요:
1. 구체성: 모양, 재질, 색상 등 세부 사항 추가
2. 명확성: 모호한 표현 대신 명확한 표현 사용
3. 구조: 대상의 구조와 비율을 명확히 설명
4. 시각적 스타일: 원하는 예술적 스타일, 렌더링 스타일 명시
5. 환경/배경: 필요시 배경이나 환경 정보 추가
"""

# 저장소 설정
DATABASE_ENABLED = True  # 데이터베이스 저장 활성화 여부

# 로깅 설정
LOGGING_ENABLED = True   # 로깅 활성화 여부
LOG_LEVEL = "INFO"       # 로그 레벨 (DEBUG, INFO, WARNING, ERROR, CRITICAL)

# API 설정
API_TIMEOUT = 30         # API 요청 타임아웃 (초) 