"""Feature flags do SGCS — ativação gradual de funcionalidades."""

from __future__ import annotations

import os
from functools import lru_cache


def _env_flag(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).lower() in {"1", "true", "yes", "on"}


@lru_cache
def get_feature_flags() -> dict[str, bool]:
    return {
        "analytics_enabled": _env_flag("FEATURE_ANALYTICS_ENABLED", False),
        "async_tasks_enabled": _env_flag("FEATURE_ASYNC_TASKS_ENABLED", True),
        "file_uploads_enabled": _env_flag("FEATURE_FILE_UPLOADS_ENABLED", True),
        "event_bus_enabled": _env_flag("FEATURE_EVENT_BUS_ENABLED", True),
        "clinical_modules_enabled": _env_flag("FEATURE_CLINICAL_MODULES_ENABLED", False),
    }


def is_feature_enabled(flag_name: str) -> bool:
    return get_feature_flags().get(flag_name, False)
