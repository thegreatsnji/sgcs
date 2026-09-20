"""Views do dashboard."""

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.views import APIView

from apps.billing.period import (
    PERIODO_HOJE,
    parse_iso_date,
    resolve_periodo,
)
from apps.dashboard.director_dashboard_service import DirectorDashboardService
from apps.dashboard.services import DashboardService
from apps.users.permissions import HasModulePermission
from core.responses import error_response, success_response


class AdminDashboardView(APIView):
    permission_classes = [HasModulePermission]
    required_permission = "dashboard.view"

    @extend_schema(tags=["Dashboard"])
    def get(self, request):
        return success_response(data=DashboardService.get_admin_summary())


class ClinicalDashboardView(APIView):
    permission_classes = [HasModulePermission]
    required_permission = "patients.view"

    @extend_schema(tags=["Dashboard"])
    def get(self, request):
        return success_response(data=DashboardService.get_clinical_summary())


class ReceptionDashboardView(APIView):
    permission_classes = [HasModulePermission]
    required_permission = "reception.view"

    @extend_schema(tags=["Dashboard"])
    def get(self, request):
        return success_response(data=DashboardService.get_reception_summary())


class ConsultationDashboardView(APIView):
    permission_classes = [HasModulePermission]
    required_permission = "appointments.view"

    @extend_schema(tags=["Dashboard"])
    def get(self, request):
        return success_response(data=DashboardService.get_consultation_summary())


class ConsultasDashboardView(APIView):
    permission_classes = [HasModulePermission]
    required_permission = "appointments.view"

    @extend_schema(tags=["Dashboard"])
    def get(self, request):
        return success_response(data=DashboardService.get_consultas_summary(user=request.user))


class LaboratoryDashboardView(APIView):
    permission_classes = [HasModulePermission]
    required_permission = "laboratory.view"

    @extend_schema(tags=["Dashboard"])
    def get(self, request):
        return success_response(data=DashboardService.get_laboratory_summary())


class BillingDashboardView(APIView):
    permission_classes = [HasModulePermission]
    required_permission = "billing.view"

    @extend_schema(tags=["Dashboard"])
    def get(self, request):
        return success_response(data=DashboardService.get_billing_summary())


class FinanceDashboardView(APIView):
    permission_classes = [HasModulePermission]
    required_permission = "finance.dashboard"

    @extend_schema(tags=["Dashboard"])
    def get(self, request):
        return success_response(data=DashboardService.get_finance_summary())


class ExecutiveDashboardView(APIView):
    permission_classes = [HasModulePermission]
    required_permission = "reports.dashboard"

    @extend_schema(tags=["Dashboard — Executivo"])
    def get(self, request):
        return success_response(
            data=DashboardService.get_executive_summary(request=request),
            message="Dashboard executivo obtido.",
        )


class NotificationsDashboardView(APIView):
    permission_classes = [HasModulePermission]
    required_permission = "notifications.view"

    @extend_schema(tags=["Dashboard — Notificações"])
    def get(self, request):
        from apps.notifications.services.notification_service import NotificationService

        return success_response(
            data=NotificationService.dashboard_kpis(),
            message="Dashboard de notificações obtido.",
        )


class SystemDashboardView(APIView):
    permission_classes = [HasModulePermission]
    required_permission = "settings.system"

    @extend_schema(tags=["Dashboard — Sistema"])
    def get(self, request):
        return success_response(
            data=DashboardService.get_system_summary(),
            message="Dashboard do sistema obtido.",
        )


class DirectorDashboardView(APIView):
    """Painel de supervisão do Director — agregados sem reception.view."""

    permission_classes = [HasModulePermission]
    required_permission = "dashboard.view"

    @extend_schema(tags=["Dashboard — Director"])
    def get(self, request):
        periodo = request.query_params.get("periodo", PERIODO_HOJE)
        try:
            data_inicio = parse_iso_date(request.query_params.get("data_inicio"))
            data_fim = parse_iso_date(request.query_params.get("data_fim"))
            inicio, fim = resolve_periodo(
                periodo, data_inicio=data_inicio, data_fim=data_fim
            )
        except ValueError as exc:
            return error_response(str(exc), status=status.HTTP_400_BAD_REQUEST)

        data = DirectorDashboardService.get_summary(data_inicio=inicio, data_fim=fim)
        data["periodo"]["modo"] = (periodo or PERIODO_HOJE).strip().lower()
        return success_response(
            data=data,
            message="Painel do Director obtido.",
        )
