"""
이 모듈은 프롬프트 개선 에이전트에서 사용하는 유틸리티 함수를 제공합니다.
"""

import re
import json
from typing import List, Dict, Any


def parse_enhanced_prompts(llm_response: str) -> List[str]:
    """
    LLM 응답에서 개선된 프롬프트 목록을 추출합니다.
    
    Args:
        llm_response (str): LLM의 응답 텍스트
        
    Returns:
        List[str]: 추출된 프롬프트 목록
    """
    # 정규 표현식을 사용하여 번호가 매겨진 프롬프트 추출
    pattern = r'\d+\.\s*(.*?)(?=\n\d+\.|\n\n|$)'
    prompts = re.findall(pattern, llm_response, re.DOTALL)
    
    # 추출된 프롬프트 정리
    cleaned_prompts = [p.strip() for p in prompts if p.strip()]
    
    return cleaned_prompts


def select_best_prompt(parsed_response: str) -> Dict[str, Any]:
    """
    LLM 응답에서 최고 점수의 프롬프트와 설명을 추출합니다.
    
    Args:
        parsed_response (str): LLM의 프롬프트 평가 응답
        
    Returns:
        Dict[str, Any]: 최고 점수 프롬프트 및 관련 정보
    """
    # 정규 표현식으로 최종 선택 프롬프트 찾기
    final_choice_pattern = r'최종\s*선택.*?:\s*(.*?)(?=\n\n|$)'
    final_match = re.search(final_choice_pattern, parsed_response, re.DOTALL)
    
    final_prompt = ""
    if final_match:
        final_prompt = final_match.group(1).strip()
    
    # 점수 패턴 찾기
    scores_pattern = r'(\d+)(?:번|\.)\s*프롬프트.*?(\d+)(?:점|\.)'
    scores = re.findall(scores_pattern, parsed_response)
    
    # 점수 딕셔너리로 변환
    scores_dict = {num: int(score) for num, score in scores}
    
    # 최고 점수의 프롬프트가 명확하게 선택되지 않았다면, 점수를 기반으로 선택
    if not final_prompt and scores_dict:
        max_score = max(scores_dict.values())
        best_prompt_nums = [num for num, score in scores_dict.items() if score == max_score]
        
        if best_prompt_nums:
            # 동점이 있는 경우 첫 번째 것 선택
            best_prompt_num = best_prompt_nums[0]
            final_prompt = f"{best_prompt_num}번 프롬프트"
    
    # 이유 찾기
    reason_pattern = r'이유.*?:(.*?)(?=\n\n|$)'
    reason_match = re.search(reason_pattern, parsed_response, re.DOTALL)
    
    reason = ""
    if reason_match:
        reason = reason_match.group(1).strip()
    else:
        # 이유가 명시적으로 제공되지 않으면 일반적인 이유 생성
        if scores_dict:
            max_score = max(scores_dict.values())
            reason = f"최고 점수({max_score})를 받은 프롬프트를 선택했습니다."
    
    return {
        "best_prompt": final_prompt,
        "scores": scores_dict,
        "reason": reason
    }


def format_enhanced_prompts_for_selection(prompts: List[str]) -> str:
    """
    선택 프로세스를 위해 개선된 프롬프트 목록을 포맷팅합니다.
    
    Args:
        prompts (List[str]): 개선된 프롬프트 목록
        
    Returns:
        str: 포맷팅된 프롬프트 목록
    """
    formatted_text = ""
    for i, prompt in enumerate(prompts, 1):
        formatted_text += f"{i}. {prompt}\n\n"
    return formatted_text.strip()


def prepare_result_for_storage(
    original_prompt: str,
    enhanced_prompts: List[str],
    selected_prompt: Dict[str, Any]
) -> Dict[str, Any]:
    """
    데이터베이스 저장을 위한 결과를 준비합니다.
    
    Args:
        original_prompt (str): 원본 프롬프트
        enhanced_prompts (List[str]): 개선된 프롬프트 목록
        selected_prompt (Dict[str, Any]): 선택된 최고 프롬프트 정보
        
    Returns:
        Dict[str, Any]: 저장할 형식으로 준비된 데이터
    """
    # 점수에서 최고 점수 프롬프트 인덱스 찾기
    scores = selected_prompt.get("scores", {})
    best_prompt_index = -1
    
    if isinstance(scores, dict) and scores:
        max_score = -1
        for num_str, score in scores.items():
            try:
                num = int(num_str) - 1  # 인덱스는 0부터 시작하므로 1을 빼줍니다
                score_val = int(score) if isinstance(score, str) else score
                if score_val > max_score and 0 <= num < len(enhanced_prompts):
                    max_score = score_val
                    best_prompt_index = num
            except (ValueError, TypeError):
                continue
    
    # 최고 점수 프롬프트 가져오기
    final_selected_prompt = ""
    if 0 <= best_prompt_index < len(enhanced_prompts):
        final_selected_prompt = enhanced_prompts[best_prompt_index]
    elif selected_prompt.get("best_prompt"):
        # 숫자가 포함된 최고 프롬프트 문자열에서 인덱스 추출 시도
        best_prompt_str = selected_prompt.get("best_prompt", "")
        match = re.search(r'(\d+)', best_prompt_str)
        if match:
            try:
                index = int(match.group(1)) - 1
                if 0 <= index < len(enhanced_prompts):
                    final_selected_prompt = enhanced_prompts[index]
            except (ValueError, IndexError):
                pass
    
    return {
        "original_prompt": original_prompt,
        "enhanced_prompts": enhanced_prompts,
        "selected_prompt": final_selected_prompt,
        "selection_reason": selected_prompt.get("reason", ""),
        "scores": selected_prompt.get("scores", {}),
        "timestamp": None  # 저장 시 설정
    } 