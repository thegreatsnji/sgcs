"""Views do módulo de relatórios."""

from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.views import APIView

from apps.reports.constants import EXPORT_FORMATS, ReportType
from apps.reports.filters import parse_report_filters
from apps.reports.permissions import ReportsPermissionMixin
from apps.reports.services.report_service import ReportService
from apps.reports.services.statistics_service import StatisticsService
from apps.users.permissions import HasModulePermission
from core.responses import error_response, success_response


class BaseReportView(ReportsPermissionMixin, APIView):
    report_type: str = ""

    @extend_schema(
        tags=["Relatórios"],
        parameters=[
            OpenApiParameter(name="periodo", description="hoje|semana|mes|ano|personalizado"),
            OpenApiParameter(name="data_inicio", description="Data início (YYYY-MM-DD)"),
            OpenApiParameter(name="data_fim", description="Data fim (YYYY-MM-DD)"),
            OpenApiParameter(name="export", description="pdf|xlsx|csv"),
            OpenApiParameter(name="medico_id", description="ID do médico"),
            OpenApiParameter(name="paciente_id", description="ID do paciente"),
            OpenApiParameter(name="estado", description="Estado"),
            OpenApiParameter(name="categoria", description="Categoria"),
        ],
    )
    def get(self, request):
        filters = parse_report_filters(request)
        export = request.query_params.get("export", "").lower()
        if export:
            try:
                return ReportService.exportar(self.report_type, export, filters, request=request)
            except ValueError as exc:
                return error_response(str(exc))
        data = ReportService.gerar(self.report_type, filters, request=request)
        return success_response(data=data, message="Relatório gerado com sucesso.")


class PatientsReportView(BaseReportView):
    report_type = ReportType.PATIENTS


class AppointmentsReportView(BaseReportView):
    report_type = ReportType.APPOINTMENTS


class ReceptionReportView(BaseReportView):
    report_type = ReportType.RECEPTION


class LaboratoryReportView(BaseReportView):
    report_type = ReportType.LABORATORY


class BillingReportView(BaseReportView):
    report_type = ReportType.BILLING


class FinanceReportView(BaseReportView):
    report_type = ReportType.FINANCE


class ChartsView(APIView):
    permission_classes = [HasModulePermission]
    required_permission = "reports.statistics"

    @extend_schema(tags=["Relatórios — Gráficos"])
    def get(self, request):
        return success_response(
            data=StatisticsService.series_temporais(),
            message="Séries temporais obtidas.",
        )


class StatisticsView(APIView):
    permission_classes = [HasModulePermission]
    required_permission = "reports.statistics"

    @extend_schema(tags=["Relatórios — Estatísticas"])
    def get(self, request):
        from apps.reports.services.cache_service import ReportsCacheService

        cached = ReportsCacheService.get_statistics("global")
        if cached:
            return success_response(data=cached)

        filters = parse_report_filters(request)
        data = {
            "pacientes": StatisticsService.relatorio_pacientes(filters)["resumo"],
            "consultas": StatisticsService.relatorio_consultas(filters)["resumo"],
            "recepcao": StatisticsService.relatorio_recepcao(filters)["resumo"],
            "laboratorio": StatisticsService.relatorio_laboratorio(filters)["resumo"],
            "faturacao": StatisticsService.relatorio_faturacao(filters)["resumo"],
            "financeiro": StatisticsService.relatorio_financeiro(filters)["resumo"],
            "graficos": StatisticsService.series_temporais(),
        }
        ReportsCacheService.set_statistics("global", data)
        return success_response(data=data, message="Estatísticas obtidas.")
