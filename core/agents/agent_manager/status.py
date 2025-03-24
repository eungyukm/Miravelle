"""
에이전트 상태 모듈

이 모듈은 AI 에이전트의 다양한 운영 상태를 정의합니다.
AgentStatus 열거형은 시스템 내 에이전트의 생명주기 상태를 추적하는 데 사용됩니다.

목적:
1. 에이전트 상태를 표준화된 방식으로 정의
2. 에이전트 관리자가 에이전트 가용성을 추적할 수 있도록 함
3. 일관된 상태 전환 흐름 제공
4. 시스템 모니터링 및 진단 지원
"""

from enum import Enum, auto


class AgentStatus(Enum):
    """
    에이전트의 운영 상태를 나타내는 열거형
    
    이 열거형은 에이전트의 현재 상태를 나타내며, 상태 변경 및 관리에 사용됩니다.
    상태는 에이전트의 가용성과 현재 작업을 결정하는 데 중요한 역할을 합니다.
    
    상태:
        IDLE: 에이전트가 작업을 수행하지 않고 새 작업을 수락할 준비가 됨
        BUSY: 에이전트가 현재 작업을 처리 중이며 새 작업을 즉시 수락할 수 없음
        ERROR: 에이전트가 오류 상태에 있으며 복구 또는 재시작이 필요함
        TERMINATED: 에이전트가 종료되어 더 이상 작업을 수행할 수 없음
        INITIALIZING: 에이전트가 초기화 중이며 아직 작업을 수락할 준비가 되지 않음
        PAUSED: 에이전트가 일시 중지되어 일시적으로 작업을 수락하지 않음
    """
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"  
    TERMINATED = "terminated"
    INITIALIZING = "initializing"
    PAUSED = "paused"