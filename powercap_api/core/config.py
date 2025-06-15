"""
FastAPI应用配置模块
"""
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置类"""
    # API配置
    api_v1_prefix: str = Field(default="/api/v1", env="API_V1_PREFIX")
    project_name: str = Field(default="PowerCapFastAPI", env="PROJECT_NAME")
    debug: bool = Field(default=False, env="DEBUG")
    port: int = Field(default=8000, env="PORT")
    
    # Redis配置
    redis_host: str = Field(default="localhost", env="REDIS_HOST")
    redis_port: int = Field(default=6379, env="REDIS_PORT")
    redis_db: int = Field(default=0, env="REDIS_DB")
    redis_password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    
    # Celery配置
    celery_broker_url: str = Field(
        default="redis://localhost:6379/0",
        env="CELERY_BROKER_URL"
    )
    celery_result_backend: str = Field(
        default="redis://localhost:6379/0",
        env="CELERY_RESULT_BACKEND"
    )
    
    # ServiceBus配置（用于微服务集成）
    service_bus_connection_string: Optional[str] = Field(
        default=None,
        env="SERVICE_BUS_CONNECTION_STRING"
    )
    service_bus_queue_name: Optional[str] = Field(
        default=None,
        env="SERVICE_BUS_QUEUE_NAME"
    )
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# 全局配置实例
settings = Settings() 