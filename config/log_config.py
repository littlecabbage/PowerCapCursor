import logging.config
from typing import Dict, Any
import os

from .env_config import get_config

def setup_logging() -> None:
    """配置日志系统"""
    config = get_config()
    
    # 确保日志目录存在
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    # 日志配置
    log_config: Dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": config.LOG_FORMAT,
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "stream": "ext://sys.stdout",
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "default",
                "filename": os.path.join(log_dir, "app.log"),
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "encoding": "utf8",
            },
            "error_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "default",
                "filename": os.path.join(log_dir, "error.log"),
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "encoding": "utf8",
            },
        },
        "loggers": {
            "": {  # root logger
                "handlers": ["console", "file"],
                "level": config.LOG_LEVEL,
            },
            "powercap_api": {
                "handlers": ["console", "file"],
                "level": config.LOG_LEVEL,
                "propagate": False,
            },
            "celery_app": {
                "handlers": ["console", "file"],
                "level": config.LOG_LEVEL,
                "propagate": False,
            },
            "error": {
                "handlers": ["error_file"],
                "level": "ERROR",
                "propagate": False,
            },
        },
    }
    
    # 应用日志配置
    logging.config.dictConfig(log_config) 