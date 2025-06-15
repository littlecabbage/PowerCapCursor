"""
任务测试模块
"""
import asyncio
from typing import Any, Dict, Generator

import pytest
from celery.result import AsyncResult

from celery_app.task_registry import app as celery_app
from celery_app.tasks.core_tasks import (DataPipelineTask, DataProcessTask,
                                       DataValidationTask, ETLWorkflowTask)
from celery_app.utils.task_utils import TaskStateManager, task_state_manager


@pytest.fixture
def task_manager() -> TaskStateManager:
    """任务管理器fixture"""
    return task_state_manager


@pytest.fixture
def celery_app_fixture() -> Generator:
    """Celery应用fixture"""
    # 配置Celery为测试模式
    celery_app.conf.update(
        task_always_eager=True,  # 同步执行任务
        task_eager_propagates=True,  # 传播异常
        broker_url='memory://',
        backend='memory://'
    )
    yield celery_app


@pytest.mark.asyncio
async def test_data_process_task(celery_app_fixture: Any) -> None:
    """测试数据处理任务"""
    # 准备测试数据
    test_data = [
        {"id": 1, "value": "test1"},
        {"id": 2, "value": "test2"}
    ]
    
    # 创建并执行任务
    task = DataProcessTask()
    result = await task.run(data=test_data)
    
    # 验证结果
    assert len(result) == len(test_data)
    for item in result:
        assert "processed" in item
        assert item["processed"] is True
        assert "timestamp" in item


@pytest.mark.asyncio
async def test_data_validation_task(celery_app_fixture: Any) -> None:
    """测试数据验证任务"""
    # 准备测试数据
    valid_data = [
        {"id": 1, "value": "valid1"},
        {"id": 2, "value": "valid2"}
    ]
    
    # 创建并执行任务
    task = DataValidationTask()
    result = await task.run(data=valid_data)
    
    # 验证结果
    assert result["valid_count"] == 2
    assert result["invalid_count"] == 0
    assert len(result["errors"]) == 0


@pytest.mark.asyncio
async def test_data_pipeline_task(celery_app_fixture: Any) -> None:
    """测试数据处理管道任务"""
    # 准备测试数据
    test_data = [
        {"id": 1, "value": "pipeline1"},
        {"id": 2, "value": "pipeline2"}
    ]
    
    # 创建并执行任务
    task = DataPipelineTask()
    results = await task.run(data=test_data)
    
    # 验证结果
    assert len(results) == 2  # 两个子任务的结果
    
    # 验证处理结果
    processed_result = results[0]
    assert len(processed_result) == len(test_data)
    for item in processed_result:
        assert item["processed"] is True
    
    # 验证验证结果
    validation_result = results[1]
    assert validation_result["valid_count"] == 2
    assert validation_result["invalid_count"] == 0


@pytest.mark.asyncio
async def test_etl_workflow_task(celery_app_fixture: Any) -> None:
    """测试ETL工作流任务"""
    # 创建并执行任务
    task = ETLWorkflowTask()
    results = await task.run(source="test_source", target="test_target")
    
    # 验证工作流步骤
    assert "extract" in results
    assert "transform" in results
    assert "load" in results
    assert "validate" in results
    
    # 验证提取结果
    extracted_data = results["extract"]
    assert len(extracted_data) == 3  # 示例数据有3条记录
    
    # 验证转换结果
    transformed_data = results["transform"]
    assert len(transformed_data) == len(extracted_data)
    for item in transformed_data:
        assert item["transformed"] is True
        assert "value_upper" in item
    
    # 验证加载结果
    load_result = results["load"]
    assert load_result["loaded_count"] == len(transformed_data)
    assert load_result["success"] is True
    
    # 验证验证结果
    validation_result = results["validate"]
    assert validation_result["valid_count"] == len(transformed_data)
    assert validation_result["invalid_count"] == 0


@pytest.mark.asyncio
async def test_task_state_management(
    celery_app_fixture: Any,
    task_manager: TaskStateManager
) -> None:
    """测试任务状态管理"""
    # 创建任务
    task = DataProcessTask()
    task_id = "test-task-id"
    
    # 更新任务状态
    task_manager.update_task_status(task_id, "STARTED")
    await asyncio.sleep(0.1)  # 模拟任务执行
    
    # 获取任务状态
    status = task_manager.get_task_status(task_id)
    assert status is not None
    assert status.task_id == task_id
    assert status.status == "STARTED"
    
    # 更新任务完成状态
    result: Dict[str, str] = {"message": "success"}
    task_manager.update_task_status(task_id, "SUCCESS", result=result)
    
    # 验证最终状态
    final_status = task_manager.get_task_status(task_id)
    assert final_status is not None
    assert final_status.status == "SUCCESS"
    assert final_status.result == str(result)
    
    # 清理任务数据
    task_manager.clean_task_data(task_id)
    cleaned_status = task_manager.get_task_status(task_id)
    assert cleaned_status is None 