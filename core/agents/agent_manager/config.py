"""
에이전트 매니저 설정 모듈

이 모듈은 에이전트 매니저 및 관리되는 에이전트들의 동작을 제어하는 설정값을 정의합니다.
대문자로 정의된 변수들은 설정값으로 사용됩니다.
"""

import os
from typing import Dict, Any

# 일반 설정
LOG_LEVEL = "INFO"  # 로깅 레벨: DEBUG, INFO, WARNING, ERROR, CRITICAL
TASK_TIMEOUT = 300  # 작업 제한 시간(초)
MAX_RETRIES = 3  # 작업 실패 시 최대 재시도 횟수
MAX_CONCURRENT_TASKS = 5  # 최대 동시 작업 수
AGENT_IDLE_TIMEOUT = 3600  # 유휴 에이전트 시간 초과(초)

# 매니저 설정
HEALTH_CHECK_INTERVAL = 60  # 상태 확인 간격(초)
API_TIMEOUT = 60  # API 요청 제한 시간(초)
QUEUE_MAX_SIZE = 100  # 작업 대기열 최대 크기
RESULT_CACHE_TTL = 3600  # 결과 캐시 유효 시간(초)

# 에이전트별 설정
# 프롬프트 향상 에이전트 설정
PROMPT_ENHANCER_CONFIG: Dict[str, Any] = {
    "DEFAULT_MODEL": "gpt-4",
    "TEMPERATURE": 0.7,
    "MAX_TOKENS": 2000,
    "TOP_P": 0.95,
    "FREQUENCY_PENALTY": 0.0,
    "PRESENCE_PENALTY": 0.0,
    "NUM_ENHANCED_PROMPTS": 3,  # 생성할 향상된 프롬프트 수
    "ENHANCEMENT_STRATEGIES": [
        "detail_addition",  # 세부 사항 추가
        "creative_expansion",  # 창의적 확장
        "technical_specificity"  # 기술적 명확화
    ],
    "PROMPT_SCORING_CRITERIA": [
        "clarity",  # 명확성
        "specificity",  # 구체성
        "creativity",  # 창의성
        "feasibility"  # 실현 가능성
    ],
    "MIN_SCORE_THRESHOLD": 7.0,  # 최소 점수 임계값(10점 만점)
    "API_ENDPOINT": "/api/prompts/enhance/",
    "DB_SAVE_ENABLED": True,  # 데이터베이스 저장 활성화 여부
}

# 모델 평가 에이전트 설정
MODEL_EVALUATOR_CONFIG: Dict[str, Any] = {
    "DEFAULT_MODEL": "gpt-4",
    "TEMPERATURE": 0.2,  # 평가에는 낮은 온도 사용
    "MAX_TOKENS": 1000,
    "EVALUATION_METRICS": [
        "visual_quality",  # 시각적 품질
        "prompt_adherence",  # 프롬프트 충실도
        "technical_accuracy",  # 기술적 정확성
        "creative_interpretation",  # 창의적 해석
        "overall_score"  # 종합 점수
    ],
    "SCORING_SCALE": 10,  # 10점 만점
    "FEEDBACK_DETAIL_LEVEL": "high",  # high/medium/low
    "REFERENCE_ENABLED": True,  # 참조 이미지 비교 활성화 여부
    "BATCH_SIZE": 5,  # 일괄 평가 크기
    "API_ENDPOINT": "/api/models/evaluate/",
    "AUTO_FEEDBACK_ENABLED": True,  # 자동 피드백 활성화 여부
}

# 자동화 에이전트 파이프라인 설정
AUTOMATION_CONFIG: Dict[str, Any] = {
    "PIPELINE_ENABLED": False,  # 파이프라인 활성화 여부
    "PIPELINE_SCHEDULE": "0 */6 * * *",  # cron 표현식 (6시간마다)
    "MAX_PIPELINE_RUNTIME": 1800,  # 최대 파이프라인 실행 시간(초)
    "ERROR_NOTIFICATION_EMAIL": os.getenv("ERROR_NOTIFICATION_EMAIL", ""),
    "SUCCESS_NOTIFICATION_EMAIL": os.getenv("SUCCESS_NOTIFICATION_EMAIL", ""),
    "PIPELINE_STEPS": [
        "prompt_generator",
        "prompt_enhancer",
        "model_generator",
        "model_evaluator"
    ],
    "DEFAULT_PIPELINE_PARAMS": {
        "num_models": 3,
        "enhancement_level": "high",
        "evaluation_required": True
    }
} 