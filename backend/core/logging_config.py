"""Configuração de logging estruturado do SGCS."""

import os
from pathlib import Path


def build_logging_config(base_dir: Path, json_format: bool = False) -> dict:
    log_dir = Path(os.getenv("LOG_DIR", base_dir / "logs"))
    log_dir.mkdir(parents=True, exist_ok=True)

    formatters = {
        "verbose": {
            "format": "{levelname} {asctime} {name} {module} {message}",
            "style": "{",
        },
    }
    if json_format:
        formatters["json"] = {
            "format": '{"time":"%(asctime)s","level":"%(levelname)s","logger":"%(name)s","module":"%(module)s","message":"%(message)s"}',
        }
    formatter_name = "json" if json_format else "verbose"

    file_handler = {
        "class": "logging.handlers.RotatingFileHandler",
        "maxBytes": int(os.getenv("LOG_MAX_BYTES", str(10 * 1024 * 1024))),
        "backupCount": int(os.getenv("LOG_BACKUP_COUNT", "5")),
        "formatter": formatter_name,
    }

    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": formatters,
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": formatter_name,
            },
            "application_file": {
                **file_handler,
                "filename": str(log_dir / "application.log"),
            },
            "security_file": {
                **file_handler,
                "filename": str(log_dir / "security.log"),
            },
            "audit_file": {
                **file_handler,
                "filename": str(log_dir / "audit.log"),
            },
            "errors_file": {
                **file_handler,
                "filename": str(log_dir / "errors.log"),
                "level": "ERROR",
            },
        },
        "loggers": {
            "django": {
                "handlers": ["console", "application_file", "errors_file"],
                "level": os.getenv("LOG_LEVEL", "INFO"),
                "propagate": False,
            },
            "apps": {
                "handlers": ["console", "application_file", "errors_file"],
                "level": os.getenv("LOG_LEVEL", "INFO"),
                "propagate": False,
            },
            "core.security": {
                "handlers": ["console", "security_file"],
                "level": "INFO",
                "propagate": False,
            },
            "apps.audit_logs": {
                "handlers": ["console", "audit_file"],
                "level": "INFO",
                "propagate": False,
            },
        },
        "root": {
            "handlers": ["console", "application_file", "errors_file"],
            "level": os.getenv("LOG_LEVEL", "INFO"),
        },
    }
