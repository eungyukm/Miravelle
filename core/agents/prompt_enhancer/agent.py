"""
이 모듈은 프롬프트 개선 에이전트의 주요 구현을 포함합니다.
"""

import logging
import os
from typing import List, Dict, Any, Optional
import json

from openai import OpenAI

from .config import (
    DEFAULT_MODEL_NAME,
    DEFAULT_TEMPERATURE,
    DEFAULT_MAX_TOKENS,
    DEFAULT_NUM_SUGGESTIONS,
    DEFAULT_BASE_PROMPT_IMPROVEMENT_INSTRUCTIONS
)
from .prompt_templates import (
    PROMPT_ENHANCER_SYSTEM_PROMPT,
    PROMPT_ENHANCER_USER_PROMPT,
    PROMPT_SELECTION_SYSTEM_PROMPT,
    PROMPT_SELECTION_USER_PROMPT
)
from .utils import (
    parse_enhanced_prompts,
    select_best_prompt,
    format_enhanced_prompts_for_selection,
    prepare_result_for_storage
)

# 로깅 설정
logger = logging.getLogger(__name__)


class PromptEnhancerAgent:
    """
    3D 모델 생성을 위한 프롬프트를 개선하는 에이전트 클래스입니다.
    """
    
    def __init__(
        self,
        model_name: str = DEFAULT_MODEL_NAME,
        temperature: float = DEFAULT_TEMPERATURE,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        num_suggestions: int = DEFAULT_NUM_SUGGESTIONS,
        api_key: Optional[str] = None
    ):
        """
        PromptEnhancerAgent 클래스의 초기화 메서드입니다.
        
        Args:
            model_name (str): 사용할 LLM 모델 이름
            temperature (float): 모델의 temperature 설정
            max_tokens (int): 최대 생성 토큰 수
            num_suggestions (int): 생성할 개선 프롬프트 개수
            api_key (Optional[str]): OpenAI API 키 (설정되지 않은 경우 환경 변수에서 가져옴)
        """
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.num_suggestions = num_suggestions
        
        # API 키가 제공되지 않은 경우 환경 변수에서 가져옴
        if not api_key:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OpenAI API 키가 설정되지 않았습니다. API 키를 제공하거나 OPENAI_API_KEY 환경 변수를 설정하세요.")
        
        # OpenAI 클라이언트 초기화
        self.client = OpenAI(api_key=api_key)
        
        logger.info(f"PromptEnhancerAgent initialized with model: {model_name}")
    
    def enhance_prompt(self, original_prompt: str) -> List[str]:
        """
        입력 프롬프트를 개선된 여러 버전으로 확장합니다.
        
        Args:
            original_prompt (str): 사용자가 입력한 원본 프롬프트
            
        Returns:
            List[str]: 개선된 프롬프트 목록
        """
        logger.info(f"Enhancing prompt: {original_prompt[:50]}...")
        
        try:
            # OpenAI API 호출
            response = self.client.chat.completions.create(
                model=self.model_name,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                messages=[
                    {"role": "system", "content": PROMPT_ENHANCER_SYSTEM_PROMPT},
                    {"role": "user", "content": PROMPT_ENHANCER_USER_PROMPT.format(original_prompt=original_prompt)}
                ]
            )
            
            # 응답 추출
            llm_response = response.choices[0].message.content
            token_usage = response.usage.total_tokens if hasattr(response, 'usage') else "N/A"
            logger.info(f"LLM usage: {token_usage} tokens")
            
            # 응답에서 개선된 프롬프트 추출
            enhanced_prompts = parse_enhanced_prompts(llm_response)
            
            logger.info(f"Generated {len(enhanced_prompts)} enhanced prompts")
            return enhanced_prompts
            
        except Exception as e:
            logger.error(f"Error enhancing prompt: {str(e)}")
            raise
    
    def select_best_enhanced_prompt(
        self, 
        enhanced_prompts: List[str], 
        original_prompt: str
    ) -> Dict[str, Any]:
        """
        개선된 프롬프트 목록에서 가장 적합한 프롬프트를 선택합니다.
        
        Args:
            enhanced_prompts (List[str]): 개선된 프롬프트 목록
            original_prompt (str): 사용자가 입력한 원본 프롬프트
            
        Returns:
            Dict[str, Any]: 선택된 최고 프롬프트와 관련 정보
        """
        logger.info("Selecting best prompt from enhanced versions...")
        
        try:
            # 프롬프트 선택을 위한 형식으로 포맷팅
            formatted_prompts = format_enhanced_prompts_for_selection(enhanced_prompts)
            
            # OpenAI API 호출
            response = self.client.chat.completions.create(
                model=self.model_name,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                messages=[
                    {"role": "system", "content": PROMPT_SELECTION_SYSTEM_PROMPT},
                    {"role": "user", "content": PROMPT_SELECTION_USER_PROMPT.format(
                        original_prompt=original_prompt,
                        enhanced_prompts=formatted_prompts
                    )}
                ]
            )
            
            # 응답 추출
            selection_response = response.choices[0].message.content
            token_usage = response.usage.total_tokens if hasattr(response, 'usage') else "N/A"
            logger.info(f"LLM usage for selection: {token_usage} tokens")
            
            # 응답에서 선택된 프롬프트 정보 추출
            selected_prompt_info = select_best_prompt(selection_response)
            logger.info(f"Selected best prompt index: {selected_prompt_info.get('best_prompt', 'None')}")
            
            return selected_prompt_info
            
        except Exception as e:
            logger.error(f"Error selecting best prompt: {str(e)}")
            raise
    
    def process(self, original_prompt: str) -> Dict[str, Any]:
        """
        입력 프롬프트를 개선하고 최적의 프롬프트를 선택하는 전체 프로세스를 실행합니다.
        
        Args:
            original_prompt (str): 사용자가 입력한 원본 프롬프트
            
        Returns:
            Dict[str, Any]: 처리 결과 (원본, 개선된 프롬프트 목록, 선택된 최고 프롬프트 등)
        """
        logger.info(f"Processing prompt: {original_prompt[:50]}...")
        
        # 프롬프트 개선
        enhanced_prompts = self.enhance_prompt(original_prompt)
        
        # 최고 프롬프트 선택
        selected_prompt = self.select_best_enhanced_prompt(enhanced_prompts, original_prompt)
        
        # 결과 준비
        result = prepare_result_for_storage(
            original_prompt=original_prompt,
            enhanced_prompts=enhanced_prompts,
            selected_prompt=selected_prompt
        )
        
        logger.info("Prompt processing completed successfully")
        return result 