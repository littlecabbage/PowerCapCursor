"""
Redis连接工具模块
"""
from typing import Optional

import redis
from pydantic import Field
from pydantic_settings import BaseSettings


class RedisSettings(BaseSettings):
    """Redis配置类"""
    host: str = Field(default="localhost", env="REDIS_HOST")
    port: int = Field(default=6379, env="REDIS_PORT")
    db: int = Field(default=0, env="REDIS_DB")
    password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")

    class Config:
        env_file = ".env"


class RedisClient:
    """Redis客户端单例类"""
    _instance: Optional[redis.Redis] = None
    _settings: RedisSettings = RedisSettings()

    @classmethod
    def get_instance(cls) -> redis.Redis:
        """获取Redis客户端实例"""
        if cls._instance is None:
            cls._instance = redis.Redis(
                host=cls._settings.host,
                port=cls._settings.port,
                db=cls._settings.db,
                password=cls._settings.password,
                decode_responses=True
            )
        return cls._instance

    @classmethod
    def close(cls) -> None:
        """关闭Redis连接"""
        if cls._instance is not None:
            cls._instance.close()
            cls._instance = None 