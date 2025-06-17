from typing import Dict, Any
from pydantic_settings import BaseSettings

class RedisSettings(BaseSettings):
    """Redis配置基类"""
    HOST: str
    PORT: int
    DB: int = 0
    PASSWORD: str = ""
    DECODE_RESPONSES: bool = True
    SOCKET_TIMEOUT: int = 5
    SOCKET_CONNECT_TIMEOUT: int = 5

class RedisSingleNodeSettings(RedisSettings):
    """单节点Redis配置"""
    class Config:
        env_prefix = "REDIS_"

class RedisClusterSettings(RedisSettings):
    """Redis集群配置"""
    CLUSTER_NODES: list[Dict[str, Any]]
    SKIP_FULL_COVERAGE_CHECK: bool = True
    
    class Config:
        env_prefix = "REDIS_CLUSTER_"

# 测试环境配置
test_redis_config = RedisSingleNodeSettings(
    HOST="localhost",
    PORT=6379,
    DB=0,
    PASSWORD="",
    DECODE_RESPONSES=True
)

# 生产环境配置
prod_redis_config = RedisClusterSettings(
    HOST="localhost",  # 默认值，实际应从环境变量获取
    PORT=6379,        # 默认值，实际应从环境变量获取
    CLUSTER_NODES=[
        {"host": "redis-node1", "port": 6379},
        {"host": "redis-node2", "port": 6379},
        {"host": "redis-node3", "port": 6379}
    ]
) 