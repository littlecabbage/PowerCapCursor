"""
状态查询API路由模块
"""
from typing import Dict

from fastapi import APIRouter, Depends
from redis import Redis

from celery_app.task_registry import app as celery_app
from powercap_api.core.dependencies import get_redis_client

router = APIRouter()


@router.get("/health")
async def health_check(redis: Redis = Depends(get_redis_client)) -> Dict[str, str]:
    """
    系统健康检查
    """
    # 检查Redis连接
    try:
        redis.ping()
        redis_status = "ok"
    except Exception:
        redis_status = "error"
    
    # 检查Celery Worker状态
    try:
        workers = celery_app.control.inspect().active()
        celery_status = "ok" if workers else "no_workers"
    except Exception:
        celery_status = "error"
    
    return {
        "status": "healthy" if all(s == "ok" for s in [redis_status, celery_status]) else "unhealthy",
        "redis": redis_status,
        "celery": celery_status
    }


@router.get("/stats")
async def get_stats(redis: Redis = Depends(get_redis_client)) -> Dict[str, int]:
    """
    获取系统统计信息
    """
    try:
        # 获取Celery统计信息
        stats = celery_app.control.inspect().stats() or {}
        total_workers = len(stats)
        
        # 获取活跃任务数
        active = celery_app.control.inspect().active() or {}
        total_active_tasks = sum(len(tasks) for tasks in active.values())
        
        # 获取已注册任务数
        registered_tasks = len(celery_app.tasks)
        
        # 获取定时任务数
        scheduled_tasks = len(celery_app.conf.beat_schedule or {})
        
        return {
            "total_workers": total_workers,
            "active_tasks": total_active_tasks,
            "registered_tasks": registered_tasks,
            "scheduled_tasks": scheduled_tasks
        }
    except Exception:
        return {
            "total_workers": 0,
            "active_tasks": 0,
            "registered_tasks": 0,
            "scheduled_tasks": 0
        } 