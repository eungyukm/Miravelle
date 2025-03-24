"""
에이전트 매니저 모듈

이 모듈은 AI 에이전트의 생명주기와 작업 실행을 관리하는 중앙 조정자를 제공합니다.
AgentManager 클래스는 싱글톤 패턴을 사용하여 시스템 전체에서 일관된 에이전트 관리를 보장합니다.

주요 기능:
1. 에이전트 등록 및 검색: 시스템에 에이전트를 등록하고 이름으로 검색
2. 작업 실행 관리: 동기 및 비동기 작업 실행, 재시도 메커니즘, 타임아웃 처리
3. 파이프라인 실행: 여러 에이전트를 통한 복잡한 워크플로우 조정
4. 상태 관리: 에이전트 상태 모니터링 및 업데이트
5. 로깅 및 성능 측정: 중앙화된 로깅 및 에이전트 성능 추적
6. 오류 처리: 일관된 오류 처리 및 복구 메커니즘
"""

import logging
import os
import importlib
import time
from typing import Dict, Any, List, Type, Optional, Tuple, Union, Callable
import traceback
import concurrent.futures
import json

from core.agents.agent_manager.status import AgentStatus
from core.agents.agent_manager.base_agent import BaseAgent
from core.agents.agent_manager.config import (
    MAX_RETRIES, 
    TASK_TIMEOUT, 
    MAX_CONCURRENT_TASKS,
    LOG_LEVEL
)


class AgentManager:
    """
    다양한 AI 에이전트를 관리하고 조율하는 매니저 클래스
    
    싱글톤 패턴을 사용하여 시스템 전체에서 하나의 인스턴스만 유지합니다.
    """
    
    _instance = None
    
    @classmethod
    def get_instance(cls) -> 'AgentManager':
        """
        에이전트 매니저의 싱글톤 인스턴스를 반환합니다.
        
        Returns:
            AgentManager: 에이전트 매니저 인스턴스
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def __init__(self):
        """
        에이전트 매니저 초기화
        
        싱글톤 패턴을 사용하므로 직접 호출하지 말고 get_instance() 메서드를 사용하세요.
        """
        if AgentManager._instance is not None:
            raise RuntimeError("AgentManager는 싱글톤입니다. get_instance()를 사용하세요.")
        
        # 로깅 설정
        self.logger = logging.getLogger("agent_manager")
        self.logger.setLevel(getattr(logging, LOG_LEVEL))
        
        # 에이전트 저장소 (이름 -> 인스턴스)
        self._agents: Dict[str, BaseAgent] = {}
        
        # 작업 풀
        self._executor = concurrent.futures.ThreadPoolExecutor(MAX_CONCURRENT_TASKS)
        self._futures: Dict[str, concurrent.futures.Future] = {}
        
        # 결과 캐시
        self._result_cache: Dict[str, Any] = {}
        
        self.logger.info("에이전트 매니저 초기화 완료")
    
    def register_agent(self, agent: BaseAgent) -> None:
        """
        에이전트를 매니저에 등록합니다.
        
        Args:
            agent (BaseAgent): 등록할 에이전트 인스턴스
            
        Raises:
            ValueError: 동일한 이름의 에이전트가 이미 등록되어 있는 경우 발생
        """
        if agent.name in self._agents:
            raise ValueError(f"동일한 이름('{agent.name}')의 에이전트가 이미 등록되어 있습니다.")
        
        self._agents[agent.name] = agent
        self.logger.info(f"에이전트 '{agent.name}' 등록 완료")
    
    def register_agent_from_class(self, agent_class: Type[BaseAgent], 
                                 name: str, config: Optional[Dict[str, Any]] = None) -> BaseAgent:
        """
        클래스에서 에이전트를 생성하고 등록합니다.
        
        Args:
            agent_class (Type[BaseAgent]): 에이전트 클래스
            name (str): 에이전트 이름
            config (Dict[str, Any], optional): 에이전트 설정
            
        Returns:
            BaseAgent: 생성 및 등록된 에이전트 인스턴스
            
        Raises:
            ValueError: 동일한 이름의 에이전트가 이미 등록되어 있는 경우 발생
        """
        if name in self._agents:
            raise ValueError(f"동일한 이름('{name}')의 에이전트가 이미 등록되어 있습니다.")
        
        agent = agent_class(name=name, config=config)
        self._agents[name] = agent
        self.logger.info(f"에이전트 '{name}' 생성 및 등록 완료")
        
        return agent
    
    def get_agent(self, agent_name: str) -> BaseAgent:
        """
        이름으로 에이전트 인스턴스를 반환합니다.
        
        Args:
            agent_name (str): 에이전트 이름
            
        Returns:
            BaseAgent: 에이전트 인스턴스
            
        Raises:
            KeyError: 지정된 이름의 에이전트가 등록되어 있지 않은 경우 발생
        """
        if agent_name not in self._agents:
            raise KeyError(f"에이전트 '{agent_name}'가 등록되어 있지 않습니다.")
        
        return self._agents[agent_name]
    
    def list_agents(self) -> List[Dict[str, Any]]:
        """
        등록된 모든 에이전트의 정보를 반환합니다.
        
        Returns:
            List[Dict[str, Any]]: 에이전트 정보 목록
        """
        agent_list = []
        
        for name, agent in self._agents.items():
            agent_info = {
                "name": name,
                "status": agent.get_status().value,
                "type": agent.__class__.__name__,
                "performance": agent.get_performance_stats()
            }
            agent_list.append(agent_info)
        
        return agent_list
    
    def update_agent_status(self, agent_name: str, status: AgentStatus) -> None:
        """
        에이전트의 상태를 업데이트합니다.
        
        Args:
            agent_name (str): 에이전트 이름
            status (AgentStatus): 새 상태
            
        Raises:
            KeyError: 지정된 이름의 에이전트가 등록되어 있지 않은 경우 발생
        """
        if agent_name not in self._agents:
            raise KeyError(f"에이전트 '{agent_name}'가 등록되어 있지 않습니다.")
        
        agent = self._agents[agent_name]
        
        # 이전 상태와 다른 경우에만 로깅
        prev_status = agent.get_status()
        if prev_status != status:
            self.logger.info(f"에이전트 '{agent_name}' 상태 변경: {prev_status} -> {status}")
            
            # 상태에 따른 추가 처리
            if status == AgentStatus.PAUSED:
                agent.pause()
            elif status == AgentStatus.IDLE and prev_status == AgentStatus.PAUSED:
                agent.resume()
            elif status == AgentStatus.TERMINATED:
                agent.terminate()
                # 작업 풀에서 실행 중인 작업 취소
                if agent_name in self._futures:
                    self._futures[agent_name].cancel()
                    del self._futures[agent_name]
            else:
                # 직접 상태 업데이트
                agent.status = status
    
    def execute_task(self, agent_name: str, task_params: Dict[str, Any], 
                     async_task: bool = False, retry_count: int = MAX_RETRIES) -> Any:
        """
        에이전트에 작업을 실행시킵니다.
        
        Args:
            agent_name (str): 에이전트 이름
            task_params (Dict[str, Any]): 작업 매개변수
            async_task (bool): 비동기 실행 여부
            retry_count (int): 오류 발생 시 재시도 횟수
            
        Returns:
            Any: 작업 결과 또는 Future 객체(비동기 실행 시)
            
        Raises:
            KeyError: 지정된 이름의 에이전트가 등록되어 있지 않은 경우 발생
            RuntimeError: 에이전트가 작업을 수행할 수 없는 상태인 경우 발생
        """
        if agent_name not in self._agents:
            raise KeyError(f"에이전트 '{agent_name}'가 등록되어 있지 않습니다.")
        
        agent = self._agents[agent_name]
        
        # 에이전트 상태 확인
        if agent.get_status() not in [AgentStatus.IDLE]:
            raise RuntimeError(f"에이전트 '{agent_name}'가 작업을 수행할 수 없는 상태입니다: {agent.get_status()}")
        
        # 비동기 실행
        if async_task:
            # 이미 실행 중인 작업이 있는지 확인
            if agent_name in self._futures and not self._futures[agent_name].done():
                raise RuntimeError(f"에이전트 '{agent_name}'에 이미 실행 중인 작업이 있습니다.")
            
            self.update_agent_status(agent_name, AgentStatus.BUSY)
            
            # 작업 제출
            future = self._executor.submit(
                self._execute_with_retry, agent, task_params, retry_count
            )
            self._futures[agent_name] = future
            
            # 작업 완료 콜백 설정
            future.add_done_callback(
                lambda f: self._handle_task_completion(agent_name, f)
            )
            
            self.logger.info(f"에이전트 '{agent_name}'에 비동기 작업 할당")
            return future
        
        # 동기 실행
        self.update_agent_status(agent_name, AgentStatus.BUSY)
        
        try:
            result = self._execute_with_retry(agent, task_params, retry_count)
            self.update_agent_status(agent_name, AgentStatus.IDLE)
            return result
        except Exception as e:
            self.update_agent_status(agent_name, AgentStatus.ERROR)
            self.logger.error(f"에이전트 '{agent_name}' 작업 실패: {str(e)}")
            raise
    
    def _execute_with_retry(self, agent: BaseAgent, task_params: Dict[str, Any], 
                           retry_count: int) -> Any:
        """
        재시도 로직이 포함된 에이전트 작업 실행
        
        Args:
            agent (BaseAgent): 에이전트 인스턴스
            task_params (Dict[str, Any]): 작업 매개변수
            retry_count (int): 재시도 횟수
            
        Returns:
            Any: 작업 결과
            
        Raises:
            Exception: 최대 재시도 횟수를 초과하여 실패한 경우 발생
        """
        last_exception = None
        
        for attempt in range(retry_count + 1):
            try:
                return agent.run(**task_params)
            except Exception as e:
                last_exception = e
                if attempt < retry_count:
                    retry_delay = min(2 ** attempt, 30)  # 지수 백오프
                    self.logger.warning(
                        f"에이전트 '{agent.name}' 작업 실패 (시도 {attempt + 1}/{retry_count + 1}): "
                        f"{str(e)}. {retry_delay}초 후 재시도합니다."
                    )
                    time.sleep(retry_delay)
                else:
                    self.logger.error(
                        f"에이전트 '{agent.name}' 작업이 최대 재시도 횟수({retry_count})를 초과하여 실패했습니다: {str(e)}"
                    )
                    break
        
        # 모든 재시도가 실패한 경우
        if last_exception:
            raise last_exception
    
    def _handle_task_completion(self, agent_name: str, future: concurrent.futures.Future) -> None:
        """
        비동기 작업 완료를 처리합니다.
        
        Args:
            agent_name (str): 에이전트 이름
            future (concurrent.futures.Future): Future 객체
        """
        # Future가 취소된 경우
        if future.cancelled():
            self.logger.info(f"에이전트 '{agent_name}'의 작업이 취소되었습니다.")
            return
        
        try:
            # 결과 추출 (예외가 발생한 경우 다시 발생)
            future.result()
            self.update_agent_status(agent_name, AgentStatus.IDLE)
            self.logger.info(f"에이전트 '{agent_name}'의 비동기 작업이 완료되었습니다.")
        except Exception as e:
            self.update_agent_status(agent_name, AgentStatus.ERROR)
            self.logger.error(
                f"에이전트 '{agent_name}'의 비동기 작업이 실패했습니다: {str(e)}\n"
                f"스택 트레이스: {traceback.format_exc()}"
            )
    
    def remove_agent(self, agent_name: str) -> None:
        """
        에이전트를 매니저에서 제거합니다.
        
        Args:
            agent_name (str): 제거할 에이전트 이름
            
        Raises:
            KeyError: 지정된 이름의 에이전트가 등록되어 있지 않은 경우 발생
            RuntimeError: 에이전트가 작업 중인 경우 발생
        """
        if agent_name not in self._agents:
            raise KeyError(f"에이전트 '{agent_name}'가 등록되어 있지 않습니다.")
        
        agent = self._agents[agent_name]
        
        # 에이전트가 작업 중인지 확인
        if agent.get_status() == AgentStatus.BUSY:
            raise RuntimeError(f"에이전트 '{agent_name}'가 작업 중입니다. 제거하기 전에 작업을 완료하거나 취소하세요.")
        
        # 에이전트 종료
        agent.terminate()
        
        # 등록 해제
        del self._agents[agent_name]
        
        # 작업 풀에서 Future 제거
        if agent_name in self._futures:
            del self._futures[agent_name]
        
        self.logger.info(f"에이전트 '{agent_name}' 제거 완료")
    
    def load_agent_from_module(self, module_path: str, class_name: str, 
                              agent_name: str, config: Optional[Dict[str, Any]] = None) -> BaseAgent:
        """
        모듈 경로에서 에이전트 클래스를 동적으로 로드하고 인스턴스를 생성하여 등록합니다.
        
        Args:
            module_path (str): 모듈 경로 (예: "core.agents.prompt_enhancer.agent")
            class_name (str): 에이전트 클래스 이름
            agent_name (str): 등록할 에이전트 이름
            config (Dict[str, Any], optional): 에이전트 설정
            
        Returns:
            BaseAgent: 생성 및 등록된 에이전트 인스턴스
            
        Raises:
            ImportError: 모듈을 가져올 수 없는 경우 발생
            AttributeError: 지정된 클래스가 모듈에 없는 경우 발생
            TypeError: 클래스가 BaseAgent를 상속하지 않는 경우 발생
        """
        try:
            # 모듈 가져오기
            module = importlib.import_module(module_path)
            
            # 클래스 가져오기
            agent_class = getattr(module, class_name)
            
            # BaseAgent를 상속하는지 확인
            if not issubclass(agent_class, BaseAgent):
                raise TypeError(f"클래스 '{class_name}'가 BaseAgent를 상속하지 않습니다.")
            
            # 에이전트 생성 및 등록
            return self.register_agent_from_class(agent_class, agent_name, config)
            
        except ImportError as e:
            self.logger.error(f"모듈 '{module_path}'를 가져올 수 없습니다: {str(e)}")
            raise
        except AttributeError as e:
            self.logger.error(f"모듈 '{module_path}'에 클래스 '{class_name}'가 없습니다: {str(e)}")
            raise
        except TypeError as e:
            self.logger.error(f"클래스 검증 실패: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"에이전트 로드 중 오류 발생: {str(e)}")
            raise
    
    def execute_pipeline(self, pipeline: List[Tuple[str, Dict[str, Any]]]) -> List[Any]:
        """
        여러 에이전트로 구성된 파이프라인을 순차적으로 실행합니다.
        
        Args:
            pipeline (List[Tuple[str, Dict[str, Any]]]): 
                (에이전트 이름, 작업 매개변수) 튜플의 목록
                
        Returns:
            List[Any]: 각 단계의 결과 목록
            
        Raises:
            Exception: 파이프라인 실행 중 오류가 발생한 경우
        """
        results = []
        
        for i, (agent_name, task_params) in enumerate(pipeline):
            try:
                self.logger.info(f"파이프라인 단계 {i+1}/{len(pipeline)} 실행: 에이전트 '{agent_name}'")
                result = self.execute_task(agent_name, task_params)
                results.append(result)
                
                # 결과를 다음 단계의 입력으로 전달
                if i < len(pipeline) - 1:
                    next_agent, next_params = pipeline[i+1]
                    if "previous_result" in next_params:
                        next_params["previous_result"] = result
                
            except Exception as e:
                self.logger.error(
                    f"파이프라인 단계 {i+1}/{len(pipeline)} 실행 중 오류 발생: {str(e)}\n"
                    f"스택 트레이스: {traceback.format_exc()}"
                )
                # 파이프라인 중단
                raise
        
        return results
    
    def terminate_all_agents(self) -> None:
        """모든 에이전트를 종료합니다."""
        for agent_name, agent in list(self._agents.items()):
            try:
                # 실행 중인 작업 취소
                if agent_name in self._futures and not self._futures[agent_name].done():
                    self._futures[agent_name].cancel()
                
                # 에이전트 종료
                agent.terminate()
                self.logger.info(f"에이전트 '{agent_name}' 종료")
                
            except Exception as e:
                self.logger.error(f"에이전트 '{agent_name}' 종료 중 오류 발생: {str(e)}")
        
        # 작업 풀 종료
        self._executor.shutdown(wait=False)
        
        # 에이전트 목록 초기화
        self._agents.clear()
        self._futures.clear()
        
        self.logger.info("모든 에이전트 종료 완료")
    
    def __del__(self):
        """소멸자"""
        try:
            # 인스턴스가 삭제될 때 모든 에이전트 종료
            self.terminate_all_agents()
        except:
            pass  # 소멸자에서는 예외를 무시