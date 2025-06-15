"""
任务注册中心模块
"""
from celery import Celery

from celery_app.celery_config import celery_config
from celery_app.tasks.core_tasks import (DataPipelineTask, DataProcessTask,
                                       DataValidationTask, ETLWorkflowTask,
                                       ExtractTask, LoadTask, TransformTask)
from celery_app.tasks.scheduled_tasks import SCHEDULED_TASKS

# 创建Celery应用实例
app = Celery("powercap")

# 加载配置
app.config_from_object(celery_config)

# 注册核心任务
CORE_TASKS = [
    DataProcessTask,
    DataValidationTask,
    DataPipelineTask,
    ETLWorkflowTask,
    ExtractTask,
    TransformTask,
    LoadTask
]

# 注册所有任务
for task_cls in [*CORE_TASKS, *SCHEDULED_TASKS]:
    task_instance = task_cls()
    app.register_task(task_instance)

# 配置定时任务
beat_schedule = {}
for task_cls in SCHEDULED_TASKS:
    if hasattr(task_cls, "periodic"):
        task_instance = task_cls()
        beat_schedule[task_instance.name] = {
            "task": task_instance.name,
            **task_instance.periodic
        }

app.conf.beat_schedule = beat_schedule 