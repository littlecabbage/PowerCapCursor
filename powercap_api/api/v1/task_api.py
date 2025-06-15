"""
任务管理API路由模块
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse

from celery_app.task_registry import app as celery_app
from celery_app.tasks.scheduled_tasks import SCHEDULED_TASKS
from celery_app.utils.task_utils import TaskStateManager
from powercap_api.core.dependencies import get_task_manager
from powercap_api.models.task_schemas import (ScheduledTaskInfo,
                                            ScheduledTaskList, TaskCreate,
                                            TaskResponse, TaskStatusResponse)

router = APIRouter()


@router.post("/tasks/run", response_model=TaskResponse, status_code=202)
async def run_task(
    task: TaskCreate,
    task_manager: TaskStateManager = Depends(get_task_manager)
) -> TaskResponse:
    """
    触发异步任务
    
    - **task_type**: 任务类型
    - **params**: 任务参数
    - **queue**: 可选的任务队列
    - **countdown**: 可选的延迟执行时间（秒）
    - **eta**: 可选的计划执行时间
    """
    try:
        # 获取任务类
        celery_task = celery_app.tasks.get(task.task_type)
        if not celery_task:
            raise HTTPException(
                status_code=404,
                detail=f"Task type '{task.task_type}' not found"
            )
        
        # 发送任务
        task_result = celery_task.apply_async(
            kwargs=task.params,
            queue=task.queue,
            countdown=task.countdown,
            eta=task.eta
        )
        
        return TaskResponse(
            task_id=task_result.id,
            task_type=task.task_type,
            params=task.params,
            status=task_result.status
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start task: {str(e)}"
        )


@router.get("/tasks/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(
    task_id: str,
    task_manager: TaskStateManager = Depends(get_task_manager)
) -> TaskStatusResponse:
    """
    获取任务状态
    
    - **task_id**: 任务ID
    """
    task_result = task_manager.get_task_status(task_id)
    if not task_result:
        raise HTTPException(
            status_code=404,
            detail=f"Task '{task_id}' not found"
        )
    
    return TaskStatusResponse(
        task_id=task_result.task_id,
        status=task_result.status,
        result=task_result.result,
        error=task_result.error
    )


@router.get("/scheduled-tasks", response_model=ScheduledTaskList)
async def list_scheduled_tasks() -> ScheduledTaskList:
    """
    列出所有定时任务
    """
    tasks: List[ScheduledTaskInfo] = []
    
    for task_cls in SCHEDULED_TASKS:
        if hasattr(task_cls, "periodic"):
            task = task_cls()
            schedule = task.periodic.get("schedule")
            queue = task.periodic.get("options", {}).get("queue", "default")
            
            task_info = ScheduledTaskInfo(
                name=task.name,
                schedule=str(schedule) if hasattr(schedule, "__str__") else schedule,
                queue=queue
            )
            tasks.append(task_info)
    
    return ScheduledTaskList(tasks=tasks)


@router.delete("/tasks/{task_id}")
async def cancel_task(
    task_id: str,
    task_manager: TaskStateManager = Depends(get_task_manager)
) -> JSONResponse:
    """
    取消任务
    
    - **task_id**: 任务ID
    """
    try:
        celery_app.control.revoke(task_id, terminate=True)
        task_manager.clean_task_data(task_id)
        return JSONResponse(
            content={"message": f"Task '{task_id}' has been cancelled"},
            status_code=200
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to cancel task: {str(e)}"
        ) 