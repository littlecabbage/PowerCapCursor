"""
任务模型模块
"""
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from celery_app.utils.task_utils import TaskStatus


class TaskBase(BaseModel):
    """任务基础模型"""
    task_type: str = Field(..., description="任务类型")
    params: Dict[str, Any] = Field(default_factory=dict, description="任务参数")


class TaskCreate(TaskBase):
    """任务创建模型"""
    queue: Optional[str] = Field(default="default", description="任务队列")
    countdown: Optional[int] = Field(default=None, description="任务延迟执行时间（秒）")
    eta: Optional[datetime] = Field(default=None, description="任务计划执行时间")


class TaskResponse(TaskBase):
    """任务响应模型"""
    task_id: str = Field(..., description="任务ID")
    status: TaskStatus = Field(..., description="任务状态")
    result: Optional[Any] = Field(default=None, description="任务结果")
    error: Optional[str] = Field(default=None, description="错误信息")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    started_at: Optional[datetime] = Field(default=None, description="开始时间")
    completed_at: Optional[datetime] = Field(default=None, description="完成时间")
    runtime: Optional[float] = Field(default=None, description="运行时间（秒）")


class TaskStatusResponse(BaseModel):
    """任务状态响应模型"""
    task_id: str = Field(..., description="任务ID")
    status: TaskStatus = Field(..., description="任务状态")
    result: Optional[Any] = Field(default=None, description="任务结果")
    error: Optional[str] = Field(default=None, description="错误信息")


class ScheduledTaskInfo(BaseModel):
    """定时任务信息模型"""
    name: str = Field(..., description="任务名称")
    schedule: Union[str, float] = Field(..., description="执行计划")
    queue: str = Field(..., description="任务队列")
    last_run: Optional[datetime] = Field(default=None, description="上次执行时间")
    next_run: Optional[datetime] = Field(default=None, description="下次执行时间")


class ScheduledTaskList(BaseModel):
    """定时任务列表模型"""
    tasks: List[ScheduledTaskInfo] = Field(..., description="定时任务列表") 