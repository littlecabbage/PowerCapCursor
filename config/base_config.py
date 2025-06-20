from typing import Any, Dict, Optional
from pydantic_settings import BaseSettings
from functools import lru_cache
import os

class BaseConfig(BaseSettings):
    """基础配置类"""
    
    # 应用配置
    APP_NAME: str = "PowerCapFastAPI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # API配置
    API_V1_PREFIX: str = "/api/v1"
    API_WORKERS: int = 1
    ALLOWED_HOSTS: list[str] = ["*"]
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Celery配置
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    CELERY_TASK_SERIALIZER: str = "json"
    CELERY_RESULT_SERIALIZER: str = "json"
    CELERY_ACCEPT_CONTENT: list[str] = ["json"]
    CELERY_TIMEZONE: str = "Asia/Shanghai"
    CELERY_CONCURRENCY: int = 2
    CELERY_TASK_SOFT_TIME_LIMIT: int = 3600  # 1小时
    CELERY_TASK_TIME_LIMIT: int = 3600 * 2   # 2小时
    
    # 安全配置
    SECRET_KEY: str = "your-secret-key-here"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24小时
    
    class Config:
        case_sensitive = True
        env_file = os.getenv("ENV_FILE", f"{os.getenv('ENVIRONMENT', 'test')}.env")

@lru_cache()
def get_base_config() -> BaseConfig:
    """获取基础配置单例"""
    return BaseConfig() 