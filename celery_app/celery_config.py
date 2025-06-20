"""
Celery配置模块
"""
from typing import Any, Dict
import os

from pydantic import Field
from pydantic_settings import BaseSettings
from config import get_celery_config


class CelerySettings(BaseSettings):
    """Celery配置类"""
    broker_url: str = Field(
        default="redis://localhost:6379/0",
        env="CELERY_BROKER_URL"
    )
    result_backend: str = Field(
        default="redis://localhost:6379/0",
        env="CELERY_RESULT_BACKEND"
    )
    task_serializer: str = Field(default="json", env="CELERY_TASK_SERIALIZER")
    result_serializer: str = Field(default="json", env="CELERY_RESULT_SERIALIZER")
    accept_content: list[str] = Field(default=["json"], env="CELERY_ACCEPT_CONTENT")
    timezone: str = Field(default="UTC", env="CELERY_TIMEZONE")
    enable_utc: bool = Field(default=True, env="CELERY_ENABLE_UTC")
    
    # 任务相关配置
    task_track_started: bool = True  # 追踪任务开始状态
    task_time_limit: int = 3600  # 任务硬时间限制（秒）
    task_soft_time_limit: int = 3540  # 任务软时间限制（秒）
    
    # 定时任务配置
    beat_schedule: Dict[str, Any] = {
        'example-task': {
            'task': 'celery_app.tasks.scheduled_tasks.example_periodic_task',
            'schedule': 300.0,  # 每5分钟执行一次
        },
    }
    
    # Worker配置
    worker_prefetch_multiplier: int = 1  # 限制每个worker的任务数
    worker_max_tasks_per_child: int = 100  # worker最大执行任务数
    worker_send_task_events: bool = True  # 发送任务事件
    
    class Config:
        env_file = os.getenv("ENV_FILE", f"{os.getenv('ENVIRONMENT', 'test')}.env")
        case_sensitive = False


settings = CelerySettings()

# Celery配置字典
celery_config = get_celery_config() 