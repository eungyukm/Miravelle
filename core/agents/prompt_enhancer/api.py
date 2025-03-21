"""
이 모듈은 프롬프트 개선 에이전트의 API 및 Django 연동을 처리합니다.
"""

import logging
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional

from django.conf import settings
from django.db import transaction

from .agent import PromptEnhancerAgent

# Django models 가져오기 (프로젝트 구조에 맞게 조정)
try:
    from prompts.models import EnhancedPrompt
    DJANGO_INTEGRATION = True
except ImportError:
    DJANGO_INTEGRATION = False
    logging.warning("Django models could not be imported. Running without DB integration.")

# 로깅 설정
logger = logging.getLogger(__name__)


class PromptEnhancerAPI:
    """
    프롬프트 개선 에이전트의 API 클래스입니다.
    이 클래스는 외부 시스템과의 연동 및 데이터 저장을 담당합니다.
    """
    
    def __init__(self):
        """
        PromptEnhancerAPI 클래스의 초기화 메서드입니다.
        """
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.warning("OPENAI_API_KEY not found in environment variables")
            
        self.agent = PromptEnhancerAgent(api_key=api_key)
        logger.info("PromptEnhancerAPI initialized")
    
    def enhance_prompt(self, original_prompt: str) -> Dict[str, Any]:
        """
        유저가 입력한 프롬프트를 개선하고 결과를 반환합니다.
        
        Args:
            original_prompt (str): 사용자가 입력한 원본 프롬프트
            
        Returns:
            Dict[str, Any]: 처리 결과
        """
        logger.info(f"API received prompt: {original_prompt[:50]}...")
        
        # 에이전트를 사용하여 프롬프트 처리
        result = self.agent.process(original_prompt)
        
        # 현재 시간 추가
        result["timestamp"] = datetime.now().isoformat()
        
        return result
    
    @staticmethod
    def save_to_database(result: Dict[str, Any]) -> Optional[int]:
        """
        프롬프트 개선 결과를 데이터베이스에 저장합니다.
        
        Args:
            result (Dict[str, Any]): 저장할 결과 데이터
            
        Returns:
            Optional[int]: 저장된 레코드의 ID 또는 None
        """
        if not DJANGO_INTEGRATION:
            logger.warning("Django integration is not available. Results not saved to DB.")
            return None
        
        try:
            with transaction.atomic():
                # JSON으로 직렬화 가능하도록 데이터 준비
                enhanced_prompts_json = json.dumps(result["enhanced_prompts"])
                scores_json = json.dumps(result.get("scores", {}))
                
                # DB에 저장
                enhanced_prompt = EnhancedPrompt.objects.create(
                    original_prompt=result["original_prompt"],
                    enhanced_prompts=enhanced_prompts_json,
                    selected_prompt=result["selected_prompt"],
                    selection_reason=result.get("selection_reason", ""),
                    scores=scores_json,
                    created_at=datetime.now()
                )
                
                logger.info(f"Saved enhanced prompt to DB with ID: {enhanced_prompt.id}")
                return enhanced_prompt.id
                
        except Exception as e:
            logger.error(f"Error saving to database: {str(e)}")
            return None
    
    def process_and_save(self, original_prompt: str) -> Dict[str, Any]:
        """
        프롬프트를 처리하고 결과를 데이터베이스에 저장합니다.
        
        Args:
            original_prompt (str): 사용자가 입력한 원본 프롬프트
            
        Returns:
            Dict[str, Any]: 처리 결과 및 저장 정보
        """
        # 프롬프트 처리
        result = self.enhance_prompt(original_prompt)
        
        # 데이터베이스에 저장
        db_id = self.save_to_database(result)
        if db_id:
            result["db_id"] = db_id
        
        return result


# 싱글톤 인스턴스 생성
prompt_enhancer_api = PromptEnhancerAPI() 