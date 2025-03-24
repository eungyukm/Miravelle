"""
에이전트 매니저 패키지

이 패키지는 AI 에이전트를 관리하고 조정하는 프레임워크를 제공합니다.
AgentManager는 다양한 에이전트들을 등록하고, 작업을 할당하며, 전체 워크플로우를 조정합니다.

주요 컴포넌트:
- AgentManager: 에이전트 관리 및 작업 조정
- BaseAgent: 모든 에이전트가 구현해야 하는 기본 인터페이스
- AgentStatus: 에이전트의 상태를 정의하는 열거형
"""

from core.agents.agent_manager.manager import AgentManager
from core.agents.agent_manager.base_agent import BaseAgent
from core.agents.agent_manager.status import AgentStatus

__all__ = ['AgentManager', 'BaseAgent', 'AgentStatus']