"""Filtros e parâmetros de relatórios."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import date, datetime, timedelta

from django.utils import timezone

from apps.reports.constants import ReportPeriod


@dataclass
class ReportFilters:
    periodo: str = ReportPeriod.MES
    data_inicio: date | None = None
    data_fim: date | None = None
    medico_id: int | None = None
    especialidade: str = ""
    paciente_id: int | None = None
    estado: str = ""
    categoria: str = ""

    def cache_key_suffix(self) -> str:
        payload = {
            "periodo": self.periodo,
            "data_inicio": self.data_inicio.isoformat() if self.data_inicio else None,
            "data_fim": self.data_fim.isoformat() if self.data_fim else None,
            "medico_id": self.medico_id,
            "especialidade": self.especialidade,
            "paciente_id": self.paciente_id,
            "estado": self.estado,
            "categoria": self.categoria,
        }
        digest = hashlib.md5(json.dumps(payload, sort_keys=True).encode()).hexdigest()[:12]
        return digest


def parse_report_filters(request) -> ReportFilters:
    periodo = request.query_params.get("periodo", ReportPeriod.MES)
    data_inicio = _parse_date(request.query_params.get("data_inicio") or request.query_params.get("from"))
    data_fim = _parse_date(request.query_params.get("data_fim") or request.query_params.get("to"))

    medico_raw = request.query_params.get("medico") or request.query_params.get("medico_id")
    paciente_raw = request.query_params.get("paciente") or request.query_params.get("paciente_id")

    filters = ReportFilters(
        periodo=periodo,
        data_inicio=data_inicio,
        data_fim=data_fim,
        medico_id=int(medico_raw) if medico_raw and medico_raw.isdigit() else None,
        especialidade=request.query_params.get("especialidade", ""),
        paciente_id=int(paciente_raw) if paciente_raw and paciente_raw.isdigit() else None,
        estado=request.query_params.get("estado", ""),
        categoria=request.query_params.get("categoria", ""),
    )
    inicio, fim = resolve_date_range(filters)
    filters.data_inicio = inicio
    filters.data_fim = fim
    return filters


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value[:10])
    except ValueError:
        return None


def resolve_date_range(filters: ReportFilters) -> tuple[date, date]:
    today = timezone.localdate()
    if filters.periodo == ReportPeriod.PERSONALIZADO and filters.data_inicio and filters.data_fim:
        return filters.data_inicio, filters.data_fim
    if filters.periodo == ReportPeriod.HOJE:
        return today, today
    if filters.periodo == ReportPeriod.SEMANA:
        start = today - timedelta(days=today.weekday())
        return start, today
    if filters.periodo == ReportPeriod.ANO:
        return date(today.year, 1, 1), today
    # Mês por defeito
    return date(today.year, today.month, 1), today


def ensure_filters(filters: ReportFilters) -> ReportFilters:
    if filters.data_inicio is None or filters.data_fim is None:
        inicio, fim = resolve_date_range(filters)
        filters.data_inicio = inicio
        filters.data_fim = fim
    return filters


def datetime_range(filters: ReportFilters) -> tuple[datetime, datetime]:
    ensure_filters(filters)
    inicio, fim = filters.data_inicio, filters.data_fim
    tz = timezone.get_current_timezone()
    start_dt = timezone.make_aware(datetime.combine(inicio, datetime.min.time()), tz)
    end_dt = timezone.make_aware(datetime.combine(fim, datetime.max.time()), tz)
    return start_dt, end_dt
