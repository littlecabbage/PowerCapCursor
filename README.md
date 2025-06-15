# PowerCapFastAPI

基于FastAPI和Celery的企业级异步任务管理系统。

## 功能特点

- 基于FastAPI的高性能异步API
- Celery分布式任务队列
- Redis作为消息代理和结果后端
- 三级任务体系（基础任务、组合任务、工作流任务）
- 完整的任务生命周期管理
- 内置定时任务支持
- 微服务集成预留接口

## 快速开始

### 本地开发环境

1. 克隆项目：
```bash
git clone https://github.com/yourusername/PowerCapFastAPI.git
cd PowerCapFastAPI
```

2. 安装依赖：
```bash
# 安装uv（如果未安装）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 创建虚拟环境并安装依赖
uv venv
source .venv/bin/activate  # Linux/macOS
# 或 .venv\Scripts\activate  # Windows
uv pip install -e ".[dev]"
```

3. 配置环境变量：
```bash
cp .env.example .env
# 根据需要修改.env文件
```

4. 启动Redis：
```bash
# 使用Docker启动Redis（推荐）
docker run -d -p 6379:6379 redis:latest

# 或使用本地Redis服务
redis-server
```

5. 启动服务：
```bash
# 终端1：启动FastAPI
uvicorn powercap_api.main:app --reload --port 8000

# 终端2：启动Celery Worker
celery -A celery_app.task_registry worker --loglevel=info

# 终端3：启动Celery Beat（如果需要定时任务）
celery -A celery_app.task_registry beat --loglevel=info
```

### Docker部署

使用Docker Compose一键部署所有服务：

```bash
docker-compose up -d
```

## API文档

启动服务后，访问以下地址查看API文档：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 新任务开发示例

1. 创建新的任务类：

```python
from celery_app.tasks.base_task import BaseTask

class MyCustomTask(BaseTask):
    name = "my_custom_task"
    
    async def run(self, *args, **kwargs):
        # 实现任务逻辑
        result = await self.process_data(*args, **kwargs)
        return result
```

2. 注册任务：

```python
# celery_app/task_registry.py
from celery_app.tasks.my_custom_task import MyCustomTask

app.register_task(MyCustomTask())
```

## 微服务集成

系统预留了ServiceBus接口用于微服务集成：

1. 在`.env`中配置ServiceBus连接信息
2. 实现`ServiceBusConnector`类进行消息队列集成
3. 在任务中使用ServiceBus发送/接收消息

## 测试

运行测试套件：

```bash
pytest
```

生成测试覆盖率报告：

```bash
pytest --cov=powercap_api --cov=celery_app --cov-report=html
```

## 项目结构

```
PowerCapFastAPI/
├── .env                    # 环境变量配置
├── pyproject.toml         # 项目依赖管理
├── celery_app/            # Celery核心包
├── powercap_api/         # FastAPI应用
└── tests/                # 测试套件
```

## 贡献指南

1. Fork项目
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 许可证

MIT 