# PowerCapFastAPI

企业级异步任务管理系统，基于 FastAPI + Celery，支持多环境分层配置、自动适配 Redis 单机/集群、统一配置入口、类型安全、易维护、易扩展。

## 主要特性
- FastAPI 高性能异步 API
- Celery 分布式任务队列，支持定时任务
- Redis 单机/集群自动适配
- 多环境分层配置（test/prod/staging 可扩展）
- 所有配置集中于 `config/settings.py`，类型安全、分组清晰、文档化
- 日志系统灵活可配，支持多级别输出
- 健康检查、自动重连、异常处理

## 目录结构
```
PowerCapFastAPI-Cursor/
├── config/           # 统一配置入口及分组文档
├── celery_app/       # Celery任务、配置与示例
├── powercap_api/     # FastAPI应用
├── utils/            # 工具类
├── tests/            # 测试用例
├── test.env          # 测试环境变量
├── prod.env          # 生产环境变量
├── Dockerfile.*      # 镜像构建文件
├── build.sh          # 镜像构建脚本
└── README.md         # 项目说明
```

## 快速上手

1. 选择环境并复制对应 env 文件：
   ```bash
   cp test.env .env  # 或 cp prod.env .env
   export ENVIRONMENT=test  # 或 prod
   ```
2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
3. 启动 Redis（本地或集群）
4. 启动 API 服务：
   ```bash
   uvicorn powercap_api.main:app --reload
   ```
5. 启动 Celery Worker：
   ```bash
   celery -A celery_app.task_registry worker --loglevel=info
   ```
6. （可选）启动 Celery Beat 定时任务：
   ```bash
   celery -A celery_app.task_registry beat --loglevel=info
   ```

## 多环境分层配置
- 所有配置集中在 `config/settings.py`，支持 test/prod/staging 等分层继承
- 自动根据 `ENVIRONMENT` 变量选择对应配置类和 env 文件
- 配置项分组清晰，类型安全，IDE 自动补全
- 支持自定义扩展环境

## 统一配置入口
- 只需 `from config import settings` 获取所有配置
- Redis/Celery/日志等均自动适配当前环境

## 常见问题
- **如何切换环境？**
  设置 `ENVIRONMENT` 环境变量并准备对应的 env 文件即可。
- **如何扩展新环境？**
  在 `config/settings.py` 新增子类并配置新 env 文件。
- **如何自定义配置项？**
  直接在 `BaseSettings` 或子类中添加字段并补充 env 文件。

## 参考文档
- [config/README.md](config/README.md) 环境变量与配置说明
- [celery_app/README.md](celery_app/README.md) Celery 配置与任务开发说明

## 功能特点

- 基于FastAPI的高性能异步API
- Celery分布式任务队列
- Redis作为消息代理和结果后端
  - 支持测试环境单机模式
  - 支持生产环境集群模式
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

4. Redis配置：

#### 测试环境（单机模式）
```bash
# 使用Docker启动Redis（推荐）
docker run -d -p 6379:6379 redis:latest

# 或使用本地Redis服务
redis-server

# 配置环境变量
ENVIRONMENT=test
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=
```

#### 生产环境（集群模式）
```bash
# 配置环境变量
ENVIRONMENT=prod
REDIS_CLUSTER_PASSWORD=your_password
REDIS_CLUSTER_NODES='[
    {"host":"redis-node1","port":6379},
    {"host":"redis-node2","port":6379},
    {"host":"redis-node3","port":6379}
]'
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

## Redis配置说明

### 配置文件结构

```
config/
└── redis_config.py       # Redis配置类
utils/
└── redis_client.py       # Redis客户端工具类
```

### Redis客户端使用示例

```python
from utils.redis_client import RedisClient

# 获取Redis客户端实例（自动根据环境选择单机或集群模式）
redis_client = RedisClient.get_instance()

# 使用Redis
redis_client.set("key", "value")
value = redis_client.get("key")
```

### 环境变量配置

测试环境配置项：
- `ENVIRONMENT`: 设置为 "test"
- `REDIS_HOST`: Redis服务器地址
- `REDIS_PORT`: Redis端口
- `REDIS_DB`: 数据库索引
- `REDIS_PASSWORD`: 密码（可选）
- `REDIS_DECODE_RESPONSES`: 是否自动解码响应
- `REDIS_SOCKET_TIMEOUT`: Socket超时时间
- `REDIS_SOCKET_CONNECT_TIMEOUT`: 连接超时时间

生产环境配置项：
- `ENVIRONMENT`: 设置为 "prod"
- `REDIS_CLUSTER_PASSWORD`: 集群密码
- `REDIS_CLUSTER_NODES`: 集群节点配置（JSON格式）
- `REDIS_CLUSTER_DECODE_RESPONSES`: 是否自动解码响应
- `REDIS_CLUSTER_SOCKET_TIMEOUT`: Socket超时时间
- `REDIS_CLUSTER_SOCKET_CONNECT_TIMEOUT`: 连接超时时间
- `REDIS_CLUSTER_SKIP_FULL_COVERAGE_CHECK`: 是否跳过完整性检查

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

## 镜像构建和部署

### 镜像构建

项目提供了两个独立的 Dockerfile：
- `Dockerfile.api`: 用于构建 API 服务镜像
- `Dockerfile.worker`: 用于构建 Celery Worker 镜像

使用构建脚本构建镜像：

```bash
# 设置环境变量（根据实际情况修改）
export IMAGE_REGISTRY="your-registry.com"
export IMAGE_PROJECT="powercap"
export VERSION="1.0.0"  # 可选，默认使用git tag

# 构建镜像
./build.sh

# 构建并推送镜像到仓库
PUSH=true ./build.sh
```

### 部署说明

1. API服务部署：
```yaml
# deployment-api.yaml 示例
apiVersion: apps/v1
kind: Deployment
metadata:
  name: powercap-api
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: api
        image: your-registry.com/powercap/powercap-api:latest
        env:
        - name: ENVIRONMENT
          value: "prod"
        - name: REDIS_CLUSTER_PASSWORD
          valueFrom:
            secretKeyRef:
              name: redis-secret
              key: password
        - name: REDIS_CLUSTER_NODES
          value: '[{"host":"redis-node1","port":6379},{"host":"redis-node2","port":6379},{"host":"redis-node3","port":6379}]'
```

2. Worker服务部署：
```yaml
# deployment-worker.yaml 示例
apiVersion: apps/v1
kind: Deployment
metadata:
  name: powercap-worker
spec:
  replicas: 2
  template:
    spec:
      containers:
      - name: worker
        image: your-registry.com/powercap/powercap-worker:latest
        env:
        - name: ENVIRONMENT
          value: "prod"
        - name: REDIS_CLUSTER_PASSWORD
          valueFrom:
            secretKeyRef:
              name: redis-secret
              key: password
        - name: REDIS_CLUSTER_NODES
          value: '[{"host":"redis-node1","port":6379},{"host":"redis-node2","port":6379},{"host":"redis-node3","port":6379}]'
```

### 环境变量配置

两个服务共享相同的环境变量配置：

1. 基础配置：
- `ENVIRONMENT`: 环境标识（"test"/"prod"）

2. Redis配置（见Redis配置章节）

3. 其他可选配置：
- `LOG_LEVEL`: 日志级别（默认："INFO"）
- `API_WORKERS`: API工作进程数（默认：1）
- `CELERY_CONCURRENCY`: Celery并发数（默认：2） 