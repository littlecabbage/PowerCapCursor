from config.settings import settings
from typing import Dict, Any

def get_celery_config() -> Dict[str, Any]:
    # 自动适配broker/backend
    if settings.CELERY_BROKER_URL:
        broker_url = settings.CELERY_BROKER_URL
    elif settings.ENVIRONMENT == "prod":
        # 自动拼接集群URL
        nodes = settings.PROD_REDIS_CLUSTER_NODES
        password = settings.PROD_REDIS_CLUSTER_PASSWORD
        nodes_str = ";".join([
            f"redis://:{password}@{node['host']}:{node['port']}/0" for node in nodes
        ])
        broker_url = f"redis-cluster://{nodes_str}"
    else:
        broker_url = f"redis://{settings.TEST_REDIS_HOST}:{settings.TEST_REDIS_PORT}/{settings.TEST_REDIS_DB}"

    if settings.CELERY_RESULT_BACKEND:
        result_backend = settings.CELERY_RESULT_BACKEND
    else:
        result_backend = broker_url

    return {
        "broker_url": broker_url,
        "result_backend": result_backend,
        "task_serializer": settings.CELERY_TASK_SERIALIZER,
        "result_serializer": settings.CELERY_RESULT_SERIALIZER,
        "accept_content": settings.CELERY_ACCEPT_CONTENT,
        "timezone": settings.CELERY_TIMEZONE,
        "enable_utc": settings.CELERY_ENABLE_UTC,
        "task_soft_time_limit": settings.CELERY_TASK_SOFT_TIME_LIMIT,
        "task_time_limit": settings.CELERY_TASK_TIME_LIMIT,
        # 其他可扩展配置
    } 