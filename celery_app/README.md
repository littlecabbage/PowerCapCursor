# Celery 使用说明

本模块为 PowerCapFastAPI 的分布式任务与定时任务实现，基于 Celery。

## 1. 配置文件说明
- 所有 Celery 相关配置均集中在 `config/settings.py`，并通过环境变量自动切换。
- 推荐通过 `.env`、`test.env`、`prod.env` 文件管理环境变量。
- 主要配置项：
  - `CELERY_BROKER_URL`、`CELERY_RESULT_BACKEND`：自动适配 Redis 单机/集群
  - `CELERY_TASK_SERIALIZER`、`CELERY_RESULT_SERIALIZER`、`CELERY_ACCEPT_CONTENT` 等序列化与内容类型
  - `CELERY_TIMEZONE`、`CELERY_ENABLE_UTC`、`CELERY_CONCURRENCY`、超时等
- 只需 `from config import get_celery_config` 获取配置字典，传递给 Celery 实例即可。

## 2. 示例任务讲解与调用

### 2.1 创建任务
```python
# celery_app/tasks/example.py
from celery import shared_task

@shared_task
def add(x, y):
    return x + y
```

### 2.2 调用任务
```python
from celery_app.tasks.example import add

# 异步调用
result = add.delay(2, 3)
print(result.get())  # 输出 5

# 同步调用（仅用于测试）
print(add(2, 3))
```

## 3. 周期任务配置逻辑与验证方式

### 3.1 配置周期任务
- 在 `celery_app/celery_config.py` 或 `celery_app/tasks/scheduled_tasks.py` 中定义 `beat_schedule`：

```python
beat_schedule = {
    'example-task': {
        'task': 'celery_app.tasks.example.add',
        'schedule': 60.0,  # 每60秒执行一次
        'args': (1, 2),
    },
}
```
- 在 Celery 启动时传递 `beat_schedule` 配置。

### 3.2 验证方式
- 启动 Celery Beat：
  ```bash
  celery -A celery_app.task_registry beat --loglevel=info
  ```
- 查看 worker 日志，确认周期任务被定时调度和执行。
- 可通过 Redis/Celery Flower 等工具监控任务状态。

## 4. Flower 可视化任务监控

Flower 是 Celery 官方推荐的分布式任务监控工具，支持 Web 可视化界面。

### 4.1 安装 Flower
```bash
pip install flower
```

### 4.2 启动 Flower
```bash
celery -A celery_app.task_registry flower --port=5555
```

### 4.3 访问监控界面
- 打开浏览器访问 [http://localhost:5555](http://localhost:5555)
- 可实时查看任务队列、任务状态、worker 状态、定时任务等

### 4.4 常见用法
- 支持任务搜索、失败重试、worker 管理、任务详情查看等
- 支持通过 `--basic_auth=user:password` 参数开启登录认证
- 更多参数见 [Flower 官方文档](https://flower.readthedocs.io/en/latest/)

## 5. 参考
- [Celery 官方文档](https://docs.celeryq.dev/en/stable/)
- [Flower 官方文档](https://flower.readthedocs.io/en/latest/)
- [config/settings.py 配置说明](../config/README.md) 