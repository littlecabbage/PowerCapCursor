"""
任务状态管理工具模块
"""
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from celery import states
from pydantic import BaseModel

from celery_app.utils.redis_conn import RedisClient


class TaskStatus(str, Enum):
    """任务状态枚举"""
    PENDING = states.PENDING  # 等待中
    STARTED = states.STARTED  # 已开始
    SUCCESS = states.SUCCESS  # 成功
    FAILURE = states.FAILURE  # 失败
    RETRY = states.RETRY     # 重试中
    REVOKED = states.REVOKED # 已取消


class TaskResult(BaseModel):
    """任务结果模型"""
    task_id: str
    status: TaskStatus
    result: Optional[Any] = None
    error: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    runtime: Optional[float] = None


class TaskStateManager:
    """任务状态管理器"""
    def __init__(self):
        self.redis = RedisClient.get_instance()
        self.task_key_prefix = "task:"
        self.task_meta_key_prefix = "task_meta:"
    
    def _get_task_key(self, task_id: str) -> str:
        """获取任务Redis键"""
        return f"{self.task_key_prefix}{task_id}"
    
    def _get_task_meta_key(self, task_id: str) -> str:
        """获取任务元数据Redis键"""
        return f"{self.task_meta_key_prefix}{task_id}"
    
    def update_task_status(
        self,
        task_id: str,
        status: TaskStatus,
        result: Optional[Any] = None,
        error: Optional[str] = None
    ) -> None:
        """更新任务状态"""
        task_key = self._get_task_key(task_id)
        task_meta_key = self._get_task_meta_key(task_id)
        
        # 更新任务状态
        self.redis.hset(task_key, "status", status.value)
        
        # 更新任务元数据
        meta: Dict[str, Any] = {
            "status": status.value,
            "update_time": datetime.utcnow().isoformat()
        }
        
        if status == TaskStatus.STARTED:
            meta["start_time"] = datetime.utcnow().isoformat()
        
        if status in (TaskStatus.SUCCESS, TaskStatus.FAILURE):
            meta["end_time"] = datetime.utcnow().isoformat()
            if "start_time" in self.redis.hgetall(task_meta_key):
                start_time = datetime.fromisoformat(self.redis.hget(task_meta_key, "start_time"))
                meta["runtime"] = (datetime.utcnow() - start_time).total_seconds()
        
        if result is not None:
            meta["result"] = str(result)
        
        if error is not None:
            meta["error"] = error
        
        self.redis.hmset(task_meta_key, meta)
    
    def get_task_status(self, task_id: str) -> Optional[TaskResult]:
        """获取任务状态"""
        task_key = self._get_task_key(task_id)
        task_meta_key = self._get_task_meta_key(task_id)
        
        if not self.redis.exists(task_key):
            return None
        
        task_data = self.redis.hgetall(task_key)
        task_meta = self.redis.hgetall(task_meta_key)
        
        result = TaskResult(
            task_id=task_id,
            status=TaskStatus(task_data.get("status", TaskStatus.PENDING)),
            result=task_meta.get("result"),
            error=task_meta.get("error"),
            start_time=datetime.fromisoformat(task_meta["start_time"]) if "start_time" in task_meta else None,
            end_time=datetime.fromisoformat(task_meta["end_time"]) if "end_time" in task_meta else None,
            runtime=float(task_meta["runtime"]) if "runtime" in task_meta else None
        )
        
        return result
    
    def clean_task_data(self, task_id: str) -> None:
        """清理任务数据"""
        self.redis.delete(self._get_task_key(task_id))
        self.redis.delete(self._get_task_meta_key(task_id))


# 全局任务状态管理器实例
task_state_manager = TaskStateManager() 