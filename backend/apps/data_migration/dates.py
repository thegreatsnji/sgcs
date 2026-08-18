"""Normalização de datas históricas — sem correcção por suposição."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any

from apps.data_migration.constants import (
    EXPECTED_DATE_MAX_OFFSET_DAYS,
    EXPECTED_DATE_MIN,
)

SUSPICIOUS_REASONS = {
    "FORA_PERIODO": "DATA_SUSPEITA",
    "FORMATO": "DATA_SUSPEITA",
    "ERRO_EXCEL": "DATA_SUSPEITA",
    "INCONSISTENTE": "DATA_SUSPEITA",
}


def _expected_max() -> date:
    return date.today() + timedelta(days=EXPECTED_DATE_MAX_OFFSET_DAYS)


def parse_date(value: Any) -> tuple[str, str, str]:
    """Devolve (data_original, data_iso YYYY-MM-DD, marcador).

    marcador é '' ou 'DATA_SUSPEITA'. Não inventa datas.
    """
    if value is None or value == "":
        return "", "", ""

    original = str(value).strip()
    parsed: date | None = None
    marker = ""

    if isinstance(value, datetime):
        parsed = value.date()
    elif isinstance(value, date):
        parsed = value
    elif isinstance(value, (int, float)) and not isinstance(value, bool):
        parsed = _from_excel_serial(value)
        if parsed is None:
            return original, "", "DATA_SUSPEITA"
        if value < 30000 or parsed.year < 1995:
            marker = "DATA_SUSPEITA"
    else:
        parsed = _from_string(original)
        if parsed is None:
            return original, "", "DATA_SUSPEITA"

    iso = parsed.isoformat()
    min_date = date.fromisoformat(EXPECTED_DATE_MIN)
    if parsed < min_date or parsed > _expected_max():
        marker = "DATA_SUSPEITA"
    return original, iso, marker


def _from_excel_serial(value: int | float) -> date | None:
    try:
        serial = int(value)
        if serial < 1 or serial > 80000:
            return None
        # Excel 1900 date system (with the known leap-year bug ignored via 1899-12-30).
        return date(1899, 12, 30) + timedelta(days=serial)
    except (OverflowError, ValueError, OSError):
        return None


def _from_string(text: str) -> date | None:
    cleaned = text.replace("\\", "/").strip()
    for fmt in (
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%d.%m.%Y",
        "%Y/%m/%d",
        "%d/%m/%y",
        "%d-%m-%y",
    ):
        try:
            parsed = datetime.strptime(cleaned[:10], fmt).date()
            if fmt.endswith("%y") and parsed.year > date.today().year + 1:
                parsed = parsed.replace(year=parsed.year - 100)
            return parsed
        except ValueError:
            continue
    return None


def dates_similar(iso_a: str, iso_b: str, max_days: int = 3) -> bool:
    if not iso_a or not iso_b:
        return False
    try:
        a, b = date.fromisoformat(iso_a), date.fromisoformat(iso_b)
    except ValueError:
        return False
    return abs((a - b).days) <= max_days
