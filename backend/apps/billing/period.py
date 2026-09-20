"""Resolução de períodos para resumo operacional de faturação (Receção)."""

from __future__ import annotations

from datetime import date, datetime, timedelta

from django.utils import timezone

PERIODO_HOJE = "hoje"
PERIODO_SEMANA = "semana"
PERIODO_MES = "mes"
PERIODO_PERSONALIZADO = "personalizado"

PERIODOS_VALIDOS = frozenset(
    {PERIODO_HOJE, PERIODO_SEMANA, PERIODO_MES, PERIODO_PERSONALIZADO}
)


def parse_iso_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value[:10])
    except ValueError as exc:
        raise ValueError("Data inválida. Use AAAA-MM-DD.") from exc


def resolve_periodo(
    periodo: str,
    *,
    data_inicio: date | None = None,
    data_fim: date | None = None,
) -> tuple[date, date]:
    """Devolve (data_inicio, data_fim) inclusivos em data local."""
    periodo = (periodo or PERIODO_HOJE).strip().lower()
    if periodo not in PERIODOS_VALIDOS:
        raise ValueError(
            "Período inválido. Use: hoje, semana, mes ou personalizado."
        )

    today = timezone.localdate()

    if periodo == PERIODO_HOJE:
        return today, today
    if periodo == PERIODO_SEMANA:
        start = today - timedelta(days=today.weekday())
        return start, today
    if periodo == PERIODO_MES:
        return date(today.year, today.month, 1), today

    # personalizado
    if data_inicio is None or data_fim is None:
        raise ValueError(
            "Para período personalizado indique data_inicio e data_fim (AAAA-MM-DD)."
        )
    if data_inicio > data_fim:
        raise ValueError("A data inicial não pode ser posterior à data final.")
    return data_inicio, data_fim


def datetime_bounds(inicio: date, fim: date) -> tuple[datetime, datetime]:
    """Início e fim inclusivos em timezone da aplicação (para filtros DateTime)."""
    tz = timezone.get_current_timezone()
    start_dt = timezone.make_aware(datetime.combine(inicio, datetime.min.time()), tz)
    end_dt = timezone.make_aware(datetime.combine(fim, datetime.max.time()), tz)
    return start_dt, end_dt
