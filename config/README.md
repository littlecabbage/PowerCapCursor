# 配置与环境变量说明

本目录为 PowerCapFastAPI 的统一配置入口，支持多环境分层继承、类型安全、自动适配。

## 1. 配置文件结构
- `settings.py`：所有配置项集中于此，分组清晰，支持 test/prod/staging 等分层继承
- `redis.py`：自动适配单机/集群
- `celery.py`：自动适配单机/集群
- `log.py`：日志系统配置

## 2. 环境变量与分层继承
- 推荐通过 `test.env`、`prod.env` 等文件管理不同环境变量
- 通过 `ENVIRONMENT` 环境变量自动选择对应配置类和 env 文件
- 可扩展更多环境，只需新增子类和 env 文件

## 3. 配置项分组与类型安全
- 所有配置项均有详细注释和类型说明，IDE 自动补全
- 支持 list/dict 类型自动转换（如 ALLOWED_HOSTS、CLUSTER_NODES）
- 配置项分为基础、Celery、Redis、日志等分组

## 4. 自动适配与统一入口
- 只需 `from config import settings` 获取所有配置
- Redis/Celery/日志等均自动适配当前环境

## 5. 常见问题
- **如何切换环境？**
  设置 `ENVIRONMENT` 环境变量并准备对应的 env 文件即可。
- **如何扩展新环境？**
  在 `settings.py` 新增子类并配置新 env 文件。
- **如何自定义配置项？**
  直接在 `BaseSettings` 或子类中添加字段并补充 env 文件。

## 6. 参考
- [settings.py](settings.py) 配置项源码与注释
- [../README.md](../README.md) 项目总览 