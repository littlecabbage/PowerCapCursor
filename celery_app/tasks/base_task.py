"""
任务基类模块
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from celery import Task

from celery_app.utils.task_utils import TaskStatus, task_state_manager


class BaseTask(Task, ABC):
    """任务基类"""
    abstract = True
    
    def __init__(self):
        self.max_retries = 3
        self.default_retry_delay = 60  # 重试延迟（秒）
    
    def on_success(self, retval: Any, task_id: str, args: tuple, kwargs: Dict[str, Any]) -> None:
        """任务成功回调"""
        super().on_success(retval, task_id, args, kwargs)
        task_state_manager.update_task_status(
            task_id=task_id,
            status=TaskStatus.SUCCESS,
            result=retval
        )
    
    def on_failure(
        self,
        exc: Exception,
        task_id: str,
        args: tuple,
        kwargs: Dict[str, Any],
        einfo: Any
    ) -> None:
        """任务失败回调"""
        super().on_failure(exc, task_id, args, kwargs, einfo)
        task_state_manager.update_task_status(
            task_id=task_id,
            status=TaskStatus.FAILURE,
            error=str(exc)
        )
    
    def on_retry(
        self,
        exc: Exception,
        task_id: str,
        args: tuple,
        kwargs: Dict[str, Any],
        einfo: Any
    ) -> None:
        """任务重试回调"""
        super().on_retry(exc, task_id, args, kwargs, einfo)
        task_state_manager.update_task_status(
            task_id=task_id,
            status=TaskStatus.RETRY,
            error=str(exc)
        )
    
    def before_start(self, task_id: str, args: tuple, kwargs: Dict[str, Any]) -> None:
        """任务开始前回调"""
        super().before_start(task_id, args, kwargs)
        task_state_manager.update_task_status(
            task_id=task_id,
            status=TaskStatus.STARTED
        )
    
    def after_return(
        self,
        status: str,
        retval: Any,
        task_id: str,
        args: tuple,
        kwargs: Dict[str, Any],
        einfo: Any
    ) -> None:
        """任务完成后回调"""
        super().after_return(status, retval, task_id, args, kwargs, einfo)
        # 可以在这里添加任务完成后的清理工作
    
    @abstractmethod
    async def run(self, *args: Any, **kwargs: Any) -> Any:
        """任务执行方法（需要子类实现）"""
        pass


class CompositeTask(BaseTask):
    """组合任务基类"""
    abstract = True
    
    def __init__(self):
        super().__init__()
        self.subtasks: list[BaseTask] = []
    
    def add_subtask(self, task: BaseTask) -> None:
        """添加子任务"""
        self.subtasks.append(task)
    
    async def run(self, *args: Any, **kwargs: Any) -> Any:
        """执行所有子任务"""
        results = []
        for subtask in self.subtasks:
            result = await subtask.run(*args, **kwargs)
            results.append(result)
        return results


class WorkflowTask(BaseTask):
    """工作流任务基类"""
    abstract = True
    
    def __init__(self):
        super().__init__()
        self.steps: Dict[str, BaseTask] = {}
        self.dependencies: Dict[str, list[str]] = {}
    
    def add_step(
        self,
        step_id: str,
        task: BaseTask,
        depends_on: Optional[list[str]] = None
    ) -> None:
        """添加工作流步骤"""
        self.steps[step_id] = task
        if depends_on:
            self.dependencies[step_id] = depends_on
    
    async def run(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """执行工作流"""
        results: Dict[str, Any] = {}
        executed = set()
        
        while len(executed) < len(self.steps):
            for step_id, task in self.steps.items():
                if step_id in executed:
                    continue
                
                # 检查依赖是否已完成
                deps = self.dependencies.get(step_id, [])
                if all(dep in executed for dep in deps):
                    result = await task.run(*args, **kwargs)
                    results[step_id] = result
                    executed.add(step_id)
        
        return results 