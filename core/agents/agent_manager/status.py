"""
에이전트 상태 모듈

에이전트의 다양한 작업 상태를 정의하는 열거형(Enum)을 제공합니다.
"""

from enum import Enum, auto


class AgentStatus(Enum):
    """
    에이전트의 상태를 나타내는 열거형
    
    에이전트의 현재 작업 상태와 가용성을 나타냅니다.
    """
    
    IDLE = "idle"  # 에이전트가 작업 준비가 되어 있음
    BUSY = "busy"  # 에이전트가 현재 작업 중임
    ERROR = "error"  # 에이전트에 오류가 발생함
    TERMINATED = "terminated"  # 에이전트가 종료됨
    INITIALIZING = "initializing"  # 에이전트가 초기화 중임
    PAUSED = "paused"  # 에이전트가 일시 중지됨