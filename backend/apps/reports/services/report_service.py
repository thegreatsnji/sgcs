"""Orquestração de relatórios, cache, auditoria e exportação."""

from __future__ import annotations

from django.http import HttpResponse

from apps.audit_logs.models import AuditAction
from apps.audit_logs.services import AuditService
from apps.reports.constants import EXPORT_CSV, EXPORT_FORMATS, EXPORT_PDF, EXPORT_XLSX, ReportType
from apps.reports.filters import ReportFilters
from apps.reports.services.cache_service import ReportsCacheService
from apps.reports.services.csv_service import CsvExportService
from apps.reports.services.excel_service import ExcelExportService
from apps.reports.services.pdf_service import PdfExportService
from apps.reports.services.statistics_service import StatisticsService
from core.events.event_bus import event_bus
from core.events.events import EventNames


class ReportService:
    GENERATORS = {
        ReportType.PATIENTS: StatisticsService.relatorio_pacientes,
        ReportType.APPOINTMENTS: StatisticsService.relatorio_consultas,
        ReportType.RECEPTION: StatisticsService.relatorio_recepcao,
        ReportType.LABORATORY: StatisticsService.relatorio_laboratorio,
        ReportType.BILLING: StatisticsService.relatorio_faturacao,
        ReportType.FINANCE: StatisticsService.relatorio_financeiro,
    }

    TITLES = {
        ReportType.PATIENTS: "Relatório de Pacientes",
        ReportType.APPOINTMENTS: "Relatório de Consultas",
        ReportType.RECEPTION: "Relatório de Receção",
        ReportType.LABORATORY: "Relatório de Laboratório",
        ReportType.BILLING: "Relatório de Faturação",
        ReportType.FINANCE: "Relatório Financeiro",
    }

    @staticmethod
    def gerar(tipo: str, filters: ReportFilters, request=None) -> dict:
        generator = ReportService.GENERATORS.get(tipo)
        if not generator:
            raise ValueError(f"Tipo de relatório inválido: {tipo}")

        filtros_hash = filters.cache_key_suffix()
        cached = ReportsCacheService.get_report(tipo, filters.periodo, filtros_hash)
        if cached:
            return cached

        data = generator(filters)
        data["series"] = StatisticsService.series_temporais()

        ReportService._auditar(
            AuditAction.REPORT_CREATED,
            request,
            tipo,
            f"Relatório {tipo} gerado.",
            {"periodo": filters.periodo},
        )
        event_bus.publish(
            EventNames.REPORT_GENERATED,
            {"tipo": tipo, "periodo": filters.periodo},
        )
        ReportsCacheService.set_report(tipo, filters.periodo, filtros_hash, data)

        from apps.reports.tasks import gerar_pdf

        gerar_pdf.delay(tipo, filters.periodo)
        return data

    @staticmethod
    def exportar(tipo: str, formato: str, filters: ReportFilters, request=None) -> HttpResponse:
        if formato not in EXPORT_FORMATS:
            raise ValueError(f"Formato inválido: {formato}")

        data = ReportService.gerar(tipo, filters, request=request)
        titulo = ReportService.TITLES.get(tipo, "Relatório SGCS")

        if formato == EXPORT_PDF:
            content = PdfExportService.export_report(titulo, data)
            content_type = "application/pdf"
            filename = f"relatorio_{tipo}.pdf"
        elif formato == EXPORT_XLSX:
            content = ExcelExportService.export_report(titulo, data)
            content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            filename = f"relatorio_{tipo}.xlsx"
        else:
            content = CsvExportService.export_report(titulo, data)
            content_type = "text/csv; charset=utf-8"
            filename = f"relatorio_{tipo}.csv"

        ReportService._auditar(
            AuditAction.REPORT_EXPORTED,
            request,
            tipo,
            f"Relatório {tipo} exportado em {formato}.",
            {"formato": formato},
        )
        event_bus.publish(
            EventNames.STATISTICS_UPDATED,
            {"tipo": tipo, "formato": formato},
        )

        from apps.reports.tasks import enviar_relatorio

        enviar_relatorio.delay(tipo, formato)

        response = HttpResponse(content, content_type=content_type)
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response

    @staticmethod
    def _auditar(action, request, resource_id, description, metadata=None):
        AuditService.log(
            action=action,
            user=getattr(request, "user", None) if request else None,
            request=request,
            description=description,
            resource_type="report",
            resource_id=str(resource_id),
            metadata=metadata or {},
        )
