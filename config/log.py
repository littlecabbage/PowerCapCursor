import logging.config
import os
from config.settings import settings

def setup_logging():
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    log_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
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
                "maxBytes": 10485760,
                "backupCount": 5,
                "encoding": "utf8",
            },
        },
        "root": {
            "handlers": ["console", "file"],
            "level": settings.LOG_LEVEL,
        },
    }
    logging.config.dictConfig(log_config) 