import os
import json
from typing import List, Dict, Any, Optional
from pydantic_settings import BaseSettings as PydanticBaseSettings
from pydantic import Field, validator

class BaseSettings(PydanticBaseSettings):
    """
    通用配置
    """
    # ========== 基础配置 ==========
    ENVIRONMENT: str = Field("test", description="环境标识，如 test/prod")
    DEBUG: bool = Field(False, description="调试模式开关")
    LOG_LEVEL: str = Field("INFO", description="日志级别")
    APP_NAME: str = Field("PowerCapFastAPI", description="应用名称")
    APP_VERSION: str = Field("1.0.0", description="应用版本")
    API_V1_PREFIX: str = Field("/api/v1", description="API前缀")
    API_WORKERS: int = Field(1, description="API进程数")
    ALLOWED_HOSTS: List[str] = Field(["*"], description="允许访问的主机列表")
    SECRET_KEY: str = Field("your-secret-key-here", description="安全密钥")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(1440, description="Token过期时间(分钟)")

    # ========== Celery 配置 ==========
    CELERY_BROKER_URL: Optional[str] = Field(None, description="Celery Broker URL，优先级高于自动拼接")
    CELERY_RESULT_BACKEND: Optional[str] = Field(None, description="Celery结果后端，优先级高于自动拼接")
    CELERY_TASK_SERIALIZER: str = Field("json", description="Celery任务序列化方式")
    CELERY_RESULT_SERIALIZER: str = Field("json", description="Celery结果序列化方式")
    CELERY_ACCEPT_CONTENT: List[str] = Field(["json"], description="Celery可接受内容类型")
    CELERY_TIMEZONE: str = Field("Asia/Shanghai", description="Celery时区")
    CELERY_ENABLE_UTC: bool = Field(True, description="Celery是否启用UTC")
    CELERY_CONCURRENCY: int = Field(2, description="Celery并发数")
    CELERY_TASK_SOFT_TIME_LIMIT: int = Field(3600, description="Celery软超时时间(秒)")
    CELERY_TASK_TIME_LIMIT: int = Field(7200, description="Celery硬超时时间(秒)")

    @validator("ALLOWED_HOSTS", pre=True)
    def parse_hosts(cls, v):
        """将字符串类型的主机列表转换为list"""
        if isinstance(v, str):
            return json.loads(v)
        return v

    @validator("CELERY_ACCEPT_CONTENT", pre=True)
    def parse_accept_content(cls, v):
        """将字符串类型的内容类型转换为list"""
        if isinstance(v, str):
            return json.loads(v)
        return v

    class Config:
        env_file = os.getenv("ENV_FILE", f"{os.getenv('ENVIRONMENT', 'test')}.env")
        case_sensitive = False

class TestSettings(BaseSettings):
    """
    测试环境专用配置
    """
    # ========== Redis 单机配置 ==========
    TEST_REDIS_HOST: str = Field("localhost", description="测试环境Redis主机")
    TEST_REDIS_PORT: int = Field(6379, description="测试环境Redis端口")
    TEST_REDIS_DB: int = Field(0, description="测试环境Redis DB编号")
    TEST_REDIS_PASSWORD: str = Field("", description="测试环境Redis密码")
    TEST_REDIS_DECODE_RESPONSES: bool = Field(True, description="测试环境Redis解码")
    TEST_REDIS_SOCKET_TIMEOUT: int = Field(5, description="测试环境Redis超时(秒)")
    TEST_REDIS_SOCKET_CONNECT_TIMEOUT: int = Field(5, description="测试环境Redis连接超时(秒)")

class ProdSettings(BaseSettings):
    """
    生产环境专用配置
    """
    # ========== Redis 集群配置 ==========
    PROD_REDIS_CLUSTER_PASSWORD: str = Field("", description="生产环境Redis集群密码")
    PROD_REDIS_CLUSTER_DECODE_RESPONSES: bool = Field(True, description="生产环境Redis集群解码")
    PROD_REDIS_CLUSTER_SOCKET_TIMEOUT: int = Field(5, description="生产环境Redis集群超时(秒)")
    PROD_REDIS_CLUSTER_SOCKET_CONNECT_TIMEOUT: int = Field(5, description="生产环境Redis集群连接超时(秒)")
    PROD_REDIS_CLUSTER_SKIP_FULL_COVERAGE_CHECK: bool = Field(True, description="生产环境Redis集群跳过覆盖检查")
    PROD_REDIS_CLUSTER_NODES: List[Dict[str, Any]] = Field([], description="生产环境Redis集群节点列表")

    @validator("PROD_REDIS_CLUSTER_NODES", pre=True)
    def parse_nodes(cls, v):
        """将字符串类型的节点列表转换为list"""
        if isinstance(v, str):
            return json.loads(v)
        return v

# 工厂函数

def get_settings():
    """
    根据ENVIRONMENT变量自动选择配置类
    """
    env = os.getenv("ENVIRONMENT", "test").lower()
    if env == "prod":
        return ProdSettings()
    return TestSettings()

settings = get_settings() 