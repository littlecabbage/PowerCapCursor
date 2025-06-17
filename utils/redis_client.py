from redis import Redis
from redis.cluster import RedisCluster
from functools import lru_cache
from typing import Union
import os

from config.redis_config import (
    RedisSingleNodeSettings,
    RedisClusterSettings,
    test_redis_config,
    prod_redis_config
)

class RedisClient:
    """Redis客户端工具类"""
    
    @staticmethod
    @lru_cache()
    def get_redis_client() -> Union[Redis, RedisCluster]:
        """
        获取Redis客户端实例
        根据环境变量ENVIRONMENT决定使用单机还是集群模式
        """
        env = os.getenv("ENVIRONMENT", "test")
        
        if env == "test":
            config = test_redis_config
            return Redis(
                host=config.HOST,
                port=config.PORT,
                db=config.DB,
                password=config.PASSWORD,
                decode_responses=config.DECODE_RESPONSES,
                socket_timeout=config.SOCKET_TIMEOUT,
                socket_connect_timeout=config.SOCKET_CONNECT_TIMEOUT
            )
        else:
            config = prod_redis_config
            return RedisCluster(
                startup_nodes=config.CLUSTER_NODES,
                decode_responses=config.DECODE_RESPONSES,
                password=config.PASSWORD,
                socket_timeout=config.SOCKET_TIMEOUT,
                socket_connect_timeout=config.SOCKET_CONNECT_TIMEOUT,
                skip_full_coverage_check=config.SKIP_FULL_COVERAGE_CHECK
            )
    
    @classmethod
    def get_instance(cls) -> Union[Redis, RedisCluster]:
        """获取Redis客户端单例"""
        return cls.get_redis_client() 