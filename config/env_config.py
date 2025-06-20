from typing import Any, Dict
from functools import lru_cache
import json
import os

from .base_config import BaseConfig
from .redis_config import (
    RedisSingleNodeSettings,
    RedisClusterSettings,
    test_redis_config,
    prod_redis_config
)

def get_env(key: str, default: Any = None) -> Any:
    return os.getenv(key, default)

class TestConfig(BaseConfig):
    """测试环境配置"""
    
    DEBUG: bool = True
    ENVIRONMENT: str = "test"
    
    # Redis配置
    REDIS_CONFIG: RedisSingleNodeSettings = test_redis_config
    
    # Celery配置优先从env读取，否则自动拼接
    CELERY_BROKER_URL: str = get_env(
        "CELERY_BROKER_URL",
        f"redis://{test_redis_config.HOST}:{test_redis_config.PORT}/{test_redis_config.DB}"
    )
    CELERY_RESULT_BACKEND: str = get_env(
        "CELERY_RESULT_BACKEND",
        f"redis://{test_redis_config.HOST}:{test_redis_config.PORT}/{test_redis_config.DB}"
    )
    
    class Config:
        env_prefix = "TEST_"

class ProdConfig(BaseConfig):
    """生产环境配置"""
    
    DEBUG: bool = False
    ENVIRONMENT: str = "prod"
    
    # Redis配置
    REDIS_CONFIG: RedisClusterSettings = prod_redis_config
    
    # Celery配置优先从env读取，否则自动拼接redis-cluster格式
    @property
    def CELERY_BROKER_URL(self) -> str:
        env_url = get_env("CELERY_BROKER_URL")
        if env_url:
            return env_url
        nodes = self.REDIS_CONFIG.CLUSTER_NODES
        password = self.REDIS_CONFIG.PASSWORD or ""
        if not nodes:
            raise ValueError("Redis cluster nodes not configured")
        nodes_str = ";".join([
            f"redis://:{password}@{node['host']}:{node['port']}/0"
            for node in nodes
        ])
        return f"redis-cluster://{nodes_str}"
    
    @property
    def CELERY_RESULT_BACKEND(self) -> str:
        env_url = get_env("CELERY_RESULT_BACKEND")
        if env_url:
            return env_url
        return self.CELERY_BROKER_URL
    
    class Config:
        env_prefix = "PROD_"

class ConfigFactory:
    """配置工厂类"""
    
    @staticmethod
    def get_config() -> BaseConfig:
        """根据环境获取对应的配置"""
        env = os.getenv("ENVIRONMENT", "test").lower()
        if env == "test":
            return TestConfig()
        elif env == "prod":
            return ProdConfig()
        else:
            raise ValueError(f"Unknown environment: {env}")

@lru_cache()
def get_config() -> BaseConfig:
    """获取配置单例"""
    return ConfigFactory.get_config() 