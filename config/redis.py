from config.settings import settings
from redis import Redis
from redis.cluster import RedisCluster
from typing import Union


def get_redis_client() -> Union[Redis, RedisCluster]:
    if settings.ENVIRONMENT == "prod":
        # 集群模式
        return RedisCluster(
            startup_nodes=settings.PROD_REDIS_CLUSTER_NODES,
            password=settings.PROD_REDIS_CLUSTER_PASSWORD,
            decode_responses=settings.PROD_REDIS_CLUSTER_DECODE_RESPONSES,
            socket_timeout=settings.PROD_REDIS_CLUSTER_SOCKET_TIMEOUT,
            socket_connect_timeout=settings.PROD_REDIS_CLUSTER_SOCKET_CONNECT_TIMEOUT,
            skip_full_coverage_check=settings.PROD_REDIS_CLUSTER_SKIP_FULL_COVERAGE_CHECK
        )
    else:
        # 单机模式
        return Redis(
            host=settings.TEST_REDIS_HOST,
            port=settings.TEST_REDIS_PORT,
            db=settings.TEST_REDIS_DB,
            password=settings.TEST_REDIS_PASSWORD,
            decode_responses=settings.TEST_REDIS_DECODE_RESPONSES,
            socket_timeout=settings.TEST_REDIS_SOCKET_TIMEOUT,
            socket_connect_timeout=settings.TEST_REDIS_SOCKET_CONNECT_TIMEOUT
        ) 