"""Dashboard executivo — KPIs agregados."""

from django.db.models import Count, F, Sum
from django.utils import timezone

from apps.reports.filters import ReportFilters
from apps.reports.services.cache_service import ReportsCacheService
from apps.reports.services.statistics_service import StatisticsService


class ReportsDashboardService:
    @staticmethod
    def get_executive_summary(request=None) -> dict:
        cached = ReportsCacheService.get_executive()
        if cached:
            return cached

        from apps.appointments.models import Appointment
        from apps.audit_logs.models import AuditAction
        from apps.audit_logs.services import AuditService
        from apps.billing.constants import PagamentoEstado
        from apps.billing.models import ItemFatura, Pagamento
        from apps.finance.services.finance_service import FinanceService
        from apps.laboratory.models import ExameLaboratorial, PedidoLaboratorial

        today = timezone.localdate()
        month_start = today.replace(day=1)
        fluxo = FinanceService.calcular_fluxo_caixa()
        filters = ReportFilters()

        consultas_stats = StatisticsService.relatorio_consultas(filters)

        novos_pacientes = StatisticsService.relatorio_pacientes(filters)["resumo"]["novos"]

        consultas_mes = Appointment.objects.filter(
            scheduled_at__date__gte=month_start,
            scheduled_at__date__lte=today,
        ).count()

        exames_mes = PedidoLaboratorial.objects.filter(created_at__date__gte=month_start).count()

        top_medicos = consultas_stats["por_medico"][:5]
        top_servicos = list(
            ItemFatura.objects.values(nome=F("servico__nome"))
            .annotate(quantidade=Sum("quantidade"))
            .order_by("-quantidade")[:5]
        )
        top_exames = list(
            ExameLaboratorial.objects.values(nome=F("nome_exame"))
            .annotate(total=Count("id"))
            .order_by("-total")[:5]
        )

        pagamentos_confirmados = Pagamento.objects.filter(estado=PagamentoEstado.CONFIRMADO).count()

        data = {
            "indicadores": {
                "receita_mensal": fluxo.get("receitas_mes", 0),
                "lucro": fluxo.get("saldo_mensal", 0),
                "pacientes_novos": novos_pacientes,
                "consultas": consultas_mes,
                "exames": exames_mes,
                "tempo_medio_consulta_min": consultas_stats["resumo"]["tempo_medio_minutos"],
                "pagamentos_confirmados": pagamentos_confirmados,
            },
            "top_medicos": top_medicos,
            "top_servicos": top_servicos,
            "top_exames": top_exames,
            "graficos": StatisticsService.series_temporais(),
        }
        ReportsCacheService.set_executive(data)

        if request:
            AuditService.log(
                action=AuditAction.DASHBOARD_VIEWED,
                user=getattr(request, "user", None),
                request=request,
                description="Dashboard executivo visualizado.",
                resource_type="dashboard",
                resource_id="executive",
            )
            from core.events.event_bus import event_bus
            from core.events.events import EventNames

            event_bus.publish(EventNames.DASHBOARD_UPDATED, {"dashboard": "executive"})

        return data
