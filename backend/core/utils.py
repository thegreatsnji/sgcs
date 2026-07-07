"""Utilitários gerais do backend."""

from datetime import date, datetime
from typing import Any


def format_date(value: date | datetime | None) -> str | None:
    if value is None:
        return None
    return value.strftime("%d/%m/%Y")


def format_datetime(value: datetime | None) -> str | None:
    if value is None:
        return None
    return value.strftime("%d/%m/%Y %H:%M")


def safe_get(data: dict[str, Any], key: str, default: Any = None) -> Any:
    return data.get(key, default)
