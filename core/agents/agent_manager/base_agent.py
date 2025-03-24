"""
기본 에이전트 모듈

모든 AI 에이전트가 상속해야 하는 기본 클래스를 정의합니다.
매니저가 에이전트를 관리하는 데 필요한 공통 인터페이스와 기능을 제공합니다.
"""

import logging
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List

from core.agents.agent_manager.status import AgentStatus


class BaseAgent(ABC):
    """
    모든 에이전트가 구현해야 하는 기본 클래스
    
    에이전트 매니저와 상호작용하는 데 필요한 공통 인터페이스와 메서드를 정의합니다.
    """
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        """
        기본 에이전트 초기화
        
        모든 에이전트에 공통적인 초기화 로직을 처리합니다.
        이름, 설정, 로깅, 상태 관리, 성능 측정 등을 설정합니다.
        
        Args:
            name (str): 에이전트 이름
            config (Dict[str, Any], optional): 에이전트 설정
        """
        self.name = name
        self.config = config or {}
        self.status = AgentStatus.INITIALIZING  # 초기화 중 상태로 시작
        
        # 로깅 설정 - 에이전트별 로거 생성
        self.logger = logging.getLogger(f"agent.{name}")
        log_level = self.config.get("LOG_LEVEL", "INFO")
        self.logger.setLevel(getattr(logging, log_level))
        
        # 성능 측정 관련 속성 - 실행 시간 및 횟수 추적
        self._last_execution_time = 0
        self._total_executions = 0
        self._execution_times = []
        
        # 초기화 완료 후 유휴 상태로 전환
        self.status = AgentStatus.IDLE
        self.logger.info(f"에이전트 '{self.name}' 초기화 완료")
    
    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        에이전트의 주요 작업을 실행합니다.
        
        모든 하위 클래스는 이 메서드를 구현해야 합니다.
        
        Args:
            **kwargs: 작업 매개변수 - 에이전트마다 다른 파라미터 지원
            
        Returns:
            Dict[str, Any]: 작업 결과 - 표준화된 형식으로 결과 반환
        """
        pass
    
    def run(self, **kwargs) -> Dict[str, Any]:
        """
        execute 메서드의 래퍼로, 성능 측정과 오류 처리를 추가합니다.
        
        Args:
            **kwargs: 작업 매개변수 - execute 메서드로 전달됨
            
        Returns:
            Dict[str, Any]: 작업 결과 - execute 메서드의 결과 반환
        """
        self.logger.info(f"에이전트 '{self.name}' 작업 시작")
        start_time = time.time()  # 시작 시간 기록
        
        try:
            # 실제 작업 실행
            result = self.execute(**kwargs)
            
            # 성능 측정 데이터 업데이트 - 성공적인 실행의 통계 수집
            execution_time = time.time() - start_time
            self._last_execution_time = execution_time
            self._total_executions += 1
            self._execution_times.append(execution_time)
            
            self.logger.info(f"에이전트 '{self.name}' 작업 완료 (소요 시간: {execution_time:.2f}초)")
            return result
            
        except Exception as e:
            # 오류 발생 시 로깅 및 재발생
            execution_time = time.time() - start_time
            self.logger.error(f"에이전트 '{self.name}' 작업 실패: {str(e)} (소요 시간: {execution_time:.2f}초)")
            raise  # 오류를 다시 발생시켜 호출자에게 전파
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """
        에이전트의 성능 통계를 반환합니다.
        
        이 메서드는 에이전트의 실행 성능에 대한 통계 정보를 제공합니다.
        - 총 실행 횟수
        - 평균 실행 시간
        - 최근 실행 시간
        - 최소/최대 실행 시간
        
        Returns:
            Dict[str, Any]: 성능 통계 데이터
        """
        if not self._execution_times:
            # 실행 기록이 없는 경우 기본값 반환
            return {
                "total_executions": 0,
                "average_time": 0,
                "last_execution_time": 0,
                "min_time": 0,
                "max_time": 0
            }
        
        # 실행 통계 계산
        return {
            "total_executions": self._total_executions,
            "average_time": sum(self._execution_times) / len(self._execution_times),
            "last_execution_time": self._last_execution_time,
            "min_time": min(self._execution_times),
            "max_time": max(self._execution_times)
        }
    
    def reset_performance_stats(self) -> None:
        """성능 통계를 초기화합니다."""
        self._last_execution_time = 0
        self._total_executions = 0
        self._execution_times = []
        self.logger.info(f"에이전트 '{self.name}' 성능 통계 초기화")
    
    def terminate(self) -> None:
        """에이전트를 종료합니다."""
        self.status = AgentStatus.TERMINATED
        self.logger.info(f"에이전트 '{self.name}' 종료")
    
    def pause(self) -> None:
        """에이전트를 일시 중지합니다."""
        self.status = AgentStatus.PAUSED
        self.logger.info(f"에이전트 '{self.name}' 일시 중지")
    
    def resume(self) -> None:
        """일시 중지된 에이전트를 재개합니다."""
        self.status = AgentStatus.IDLE
        self.logger.info(f"에이전트 '{self.name}' 재개")
    
    def get_status(self) -> AgentStatus:
        """에이전트의 현재 상태를 반환합니다."""
        return self.status
    
    def __str__(self) -> str:
        """에이전트 문자열 표현"""
        return f"{self.name} Agent (Status: {self.status.value})" 