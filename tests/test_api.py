"""
API测试模块
"""
from typing import Any, Dict, Generator

import pytest
from fastapi.testclient import TestClient
from redis import Redis

from celery_app.task_registry import app as celery_app
from celery_app.utils.redis_conn import RedisClient
from powercap_api.main import app


@pytest.fixture
def client() -> Generator:
    """测试客户端fixture"""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def redis_client() -> Generator:
    """Redis客户端fixture"""
    client = RedisClient.get_instance()
    yield client
    client.flushdb()  # 清理测试数据
    RedisClient.close()


@pytest.fixture
def celery_app_fixture() -> Generator:
    """Celery应用fixture"""
    celery_app.conf.update(
        task_always_eager=True,
        task_eager_propagates=True,
        broker_url='memory://',
        backend='memory://'
    )
    yield celery_app


def test_root(client: TestClient) -> None:
    """测试根路由"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_health_check(
    client: TestClient,
    redis_client: Redis,
    celery_app_fixture: Any
) -> None:
    """测试健康检查接口"""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "redis" in data
    assert "celery" in data


def test_get_stats(
    client: TestClient,
    redis_client: Redis,
    celery_app_fixture: Any
) -> None:
    """测试统计信息接口"""
    response = client.get("/api/v1/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_workers" in data
    assert "active_tasks" in data
    assert "registered_tasks" in data
    assert "scheduled_tasks" in data


def test_run_task(
    client: TestClient,
    redis_client: Redis,
    celery_app_fixture: Any
) -> None:
    """测试运行任务接口"""
    task_data = {
        "task_type": "data_process_task",
        "params": {
            "data": [
                {"id": 1, "value": "test1"},
                {"id": 2, "value": "test2"}
            ]
        }
    }
    
    response = client.post("/api/v1/tasks/run", json=task_data)
    assert response.status_code == 202
    data = response.json()
    assert "task_id" in data
    assert data["task_type"] == task_data["task_type"]


def test_get_task_status(
    client: TestClient,
    redis_client: Redis,
    celery_app_fixture: Any
) -> None:
    """测试获取任务状态接口"""
    # 首先创建一个任务
    task_data = {
        "task_type": "data_process_task",
        "params": {
            "data": [{"id": 1, "value": "test"}]
        }
    }
    create_response = client.post("/api/v1/tasks/run", json=task_data)
    task_id = create_response.json()["task_id"]
    
    # 获取任务状态
    response = client.get(f"/api/v1/tasks/{task_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["task_id"] == task_id
    assert "status" in data


def test_list_scheduled_tasks(
    client: TestClient,
    celery_app_fixture: Any
) -> None:
    """测试列出定时任务接口"""
    response = client.get("/api/v1/scheduled-tasks")
    assert response.status_code == 200
    data = response.json()
    assert "tasks" in data
    tasks = data["tasks"]
    assert isinstance(tasks, list)
    if tasks:  # 如果有定时任务
        task = tasks[0]
        assert "name" in task
        assert "schedule" in task
        assert "queue" in task


def test_cancel_task(
    client: TestClient,
    redis_client: Redis,
    celery_app_fixture: Any
) -> None:
    """测试取消任务接口"""
    # 首先创建一个任务
    task_data = {
        "task_type": "data_process_task",
        "params": {
            "data": [{"id": 1, "value": "test"}]
        }
    }
    create_response = client.post("/api/v1/tasks/run", json=task_data)
    task_id = create_response.json()["task_id"]
    
    # 取消任务
    response = client.delete(f"/api/v1/tasks/{task_id}")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert task_id in data["message"] 