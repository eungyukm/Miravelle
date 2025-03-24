"""
에이전트 매니저 사용 예제

이 파일은 에이전트 매니저와 에이전트를 생성 및 사용하는 방법을 보여주는 예제 코드를 제공합니다.
새로운 에이전트를 개발하고 시스템에 통합하려는 개발자에게 참조 자료로 활용할 수 있습니다.

사용 예제:
1. 커스텀 에이전트 생성
2. 에이전트 등록 및 사용
3. 비동기 작업 실행
4. 파이프라인 생성
5. 에러 처리
"""

import logging
import time
from typing import Dict, Any

from core.agents.agent_manager import AgentManager, BaseAgent, AgentStatus
from core.agents.agent_manager.config import PROMPT_ENHANCER_CONFIG


# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SimplePromptEnhancer(BaseAgent):
    """
    프롬프트 향상 기능을 제공하는 간단한 예제 에이전트
    
    BaseAgent를 상속받아 execute 메서드를 구현한 간단한 에이전트입니다.
    """
    
    def __init__(self, name: str):
        """에이전트 초기화"""
        super().__init__(name, config=PROMPT_ENHANCER_CONFIG)
        self.logger.info(f"프롬프트 향상 에이전트 '{name}' 초기화 완료")
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        프롬프트 향상 작업 실행
        
        Args:
            prompt (str): 원본 프롬프트
            
        Returns:
            Dict[str, Any]: 향상된 프롬프트 및 관련 데이터
        """
        prompt = kwargs.get("prompt", "")
        if not prompt:
            self.logger.error("프롬프트가 제공되지 않았습니다")
            return {"error": "프롬프트가 필요합니다", "success": False}
        
        self.logger.info(f"프롬프트 향상 시작: '{prompt[:50]}...'")
        
        # 실제 에이전트는 여기서 AI 모델 API 호출 등의 작업을 수행
        # 예제에서는 간단한 문자열 조작으로 대체
        enhanced_prompt = f"{prompt} (더 자세한 색상, 재질, 조명 및 기하학적 세부 정보 포함)"
        
        # 지연 시뮬레이션 - 실제 AI 처리 시간 모방
        time.sleep(1)
        
        result = {
            "original_prompt": prompt,
            "enhanced_prompt": enhanced_prompt,
            "enhancement_method": "detail_addition",
            "score": 8.5,
            "success": True
        }
        
        self.logger.info(f"프롬프트 향상 완료: '{enhanced_prompt[:50]}...'")
        return result


def example_custom_agent_creation():
    """커스텀 에이전트 생성 및 사용 예제"""
    logger.info("=== 커스텀 에이전트 생성 예제 ===")
    
    # 에이전트 인스턴스 생성
    enhancer = SimplePromptEnhancer("sample_enhancer")
    
    # 에이전트 직접 사용
    result = enhancer.run(prompt="파란색 공")
    
    logger.info(f"직접 실행 결과: {result['enhanced_prompt']}")
    logger.info("=== 커스텀 에이전트 생성 예제 종료 ===\n")


def example_agent_manager_usage():
    """에이전트 매니저를 통한 에이전트 등록 및 사용 예제"""
    logger.info("=== 에이전트 매니저 사용 예제 ===")
    
    # 에이전트 매니저 인스턴스 가져오기
    manager = AgentManager.get_instance()
    
    # 에이전트 클래스 등록
    manager.register_agent_class("prompt_enhancer", SimplePromptEnhancer)
    
    # 등록된 클래스로부터 에이전트 인스턴스 획득
    # 이 방식으로 동일한 에이전트 클래스의 여러 인스턴스를 다른 이름으로 생성 가능
    manager.get_agent("enhancer1", agent_type="prompt_enhancer")
    
    # 에이전트를 통한 작업 실행
    result = manager.execute_task(
        agent_name="enhancer1",
        prompt="빨간색 상자"
    )
    
    logger.info(f"매니저를 통한 실행 결과: {result['enhanced_prompt']}")
    
    # 등록된 모든 에이전트 확인
    agents = manager.list_agents()
    logger.info(f"등록된 에이전트: {agents}")
    
    # 에이전트 상태 변경 예제
    manager.update_agent_status("enhancer1", AgentStatus.PAUSED)
    logger.info(f"에이전트 상태: {manager.get_agent_status('enhancer1')}")
    
    # 에이전트 다시 활성화
    manager.update_agent_status("enhancer1", AgentStatus.IDLE)
    
    logger.info("=== 에이전트 매니저 사용 예제 종료 ===\n")


def example_async_task_execution():
    """비동기 작업 실행 예제"""
    logger.info("=== 비동기 작업 실행 예제 ===")
    
    manager = AgentManager.get_instance()
    
    # 비동기 작업 시작
    task_ids = []
    for i in range(3):
        prompt = f"프롬프트 #{i+1}: 3D 모델"
        task_id = manager.execute_task_async(
            agent_name="enhancer1",
            prompt=prompt
        )
        task_ids.append(task_id)
        logger.info(f"작업 #{i+1} 시작됨 - ID: {task_id}")
    
    # 작업 완료 대기 및 결과 수집
    for task_id in task_ids:
        result = manager.get_task_result(task_id, wait=True)
        logger.info(f"작업 {task_id} 결과: {result['enhanced_prompt']}")
    
    logger.info("=== 비동기 작업 실행 예제 종료 ===\n")


def example_pipeline_execution():
    """파이프라인 실행 예제"""
    logger.info("=== 파이프라인 실행 예제 ===")
    
    manager = AgentManager.get_instance()
    
    # 간단한 파이프라인 정의 - 같은 에이전트를 여러 단계로 사용
    pipeline = [
        {
            "agent": "enhancer1",
            "params": {"prompt": "초기 프롬프트: 파란 구슬"}
        },
        {
            "agent": "enhancer1",
            "params": {}  # 이전 단계의 결과를 입력으로 사용
        }
    ]
    
    # 파이프라인 실행
    result = manager.execute_pipeline(pipeline)
    
    logger.info(f"파이프라인 최종 결과: {result['enhanced_prompt']}")
    logger.info("=== 파이프라인 실행 예제 종료 ===\n")


def example_error_handling():
    """에러 처리 예제"""
    logger.info("=== 에러 처리 예제 ===")
    
    manager = AgentManager.get_instance()
    
    # 의도적으로 에러 발생시키기 (필수 매개변수 누락)
    try:
        result = manager.execute_task(
            agent_name="enhancer1",
            # prompt 매개변수 누락
        )
    except Exception as e:
        logger.info(f"예상된 에러 발생: {str(e)}")
    
    # 존재하지 않는 에이전트 사용 시도
    try:
        result = manager.execute_task(
            agent_name="non_existent_agent",
            prompt="테스트"
        )
    except Exception as e:
        logger.info(f"존재하지 않는 에이전트 에러: {str(e)}")
    
    logger.info("=== 에러 처리 예제 종료 ===\n")


def run_all_examples():
    """모든 예제 실행"""
    logger.info("에이전트 매니저 예제 시작")
    
    # 각 예제 순차적으로 실행
    example_custom_agent_creation()
    example_agent_manager_usage()
    example_async_task_execution()
    example_pipeline_execution()
    example_error_handling()
    
    # 정리
    manager = AgentManager.get_instance()
    manager.terminate_all_agents()
    
    logger.info("모든 예제 실행 완료")


if __name__ == "__main__":
    run_all_examples() 