"""Agregações estatísticas para relatórios e BI."""

from __future__ import annotations

from datetime import timedelta

from django.db.models import Avg, Count, F, Q, Sum
from django.db.models.functions import TruncDate, TruncMonth
from django.utils import timezone

from apps.reports.filters import ReportFilters, datetime_range, ensure_filters


class StatisticsService:
    @staticmethod
    def relatorio_pacientes(filters: ReportFilters) -> dict:
        from apps.patients.models import Patient

        ensure_filters(filters)
        qs = Patient.objects.filter(deleted_at__isnull=True)
        start_dt, end_dt = datetime_range(filters)
        novos = qs.filter(created_at__range=(start_dt, end_dt)).count()

        por_sexo = list(qs.values("gender").annotate(total=Count("id")).order_by("-total"))
        por_cidade = list(
            qs.exclude(address_city="")
            .values("address_city")
            .annotate(total=Count("id"))
            .order_by("-total")[:10]
        )
        por_nacionalidade = list(
            qs.exclude(nationality="")
            .values("nationality")
            .annotate(total=Count("id"))
            .order_by("-total")[:10]
        )

        faixas = {"0-17": 0, "18-35": 0, "36-55": 0, "56+": 0}
        today = timezone.localdate()
        for p in qs.only("birth_date"):
            idade = (today - p.birth_date).days // 365
            if idade < 18:
                faixas["0-17"] += 1
            elif idade <= 35:
                faixas["18-35"] += 1
            elif idade <= 55:
                faixas["36-55"] += 1
            else:
                faixas["56+"] += 1

        return {
            "tipo": "pacientes",
            "periodo": filters.periodo,
            "data_inicio": filters.data_inicio.isoformat(),
            "data_fim": filters.data_fim.isoformat(),
            "resumo": {
                "total": qs.count(),
                "novos": novos,
                "activos": qs.filter(is_active=True).count(),
                "inactivos": qs.filter(is_active=False).count(),
            },
            "demografia": {
                "por_sexo": por_sexo,
                "faixa_etaria": faixas,
                "por_cidade": por_cidade,
                "por_nacionalidade": por_nacionalidade,
            },
        }

    @staticmethod
    def relatorio_consultas(filters: ReportFilters) -> dict:
        from apps.appointments.constants import AppointmentStatus
        from apps.appointments.models import Appointment
        from django.db.models import DurationField, ExpressionWrapper

        ensure_filters(filters)
        start_dt, end_dt = datetime_range(filters)
        qs = Appointment.objects.filter(scheduled_at__range=(start_dt, end_dt))
        if filters.medico_id:
            qs = qs.filter(doctor_id=filters.medico_id)
        if filters.paciente_id:
            qs = qs.filter(patient_id=filters.paciente_id)
        if filters.estado:
            qs = qs.filter(status=filters.estado)

        por_medico = list(
            qs.filter(doctor__isnull=False)
            .values(medico=F("doctor__first_name"), apelido=F("doctor__last_name"))
            .annotate(total=Count("id"))
            .order_by("-total")[:10]
        )
        for item in por_medico:
            item["medico"] = f"{item.pop('medico', '')} {item.pop('apelido', '')}".strip()

        duracao = ExpressionWrapper(
            F("completed_at") - F("started_at"),
            output_field=DurationField(),
        )
        tempo_medio = qs.filter(
            started_at__isnull=False,
            completed_at__isnull=False,
        ).aggregate(media=Avg(duracao))["media"]

        tempo_minutos = 0.0
        if tempo_medio:
            tempo_minutos = round(tempo_medio.total_seconds() / 60, 1)

        hoje = timezone.localdate()
        return {
            "tipo": "consultas",
            "periodo": filters.periodo,
            "data_inicio": filters.data_inicio.isoformat(),
            "data_fim": filters.data_fim.isoformat(),
            "resumo": {
                "total": qs.count(),
                "hoje": Appointment.objects.filter(consultation_date=hoje).count(),
                "semana": Appointment.objects.filter(
                    scheduled_at__date__gte=hoje - timedelta(days=hoje.weekday()),
                    scheduled_at__date__lte=hoje,
                ).count(),
                "mes": Appointment.objects.filter(
                    scheduled_at__year=hoje.year,
                    scheduled_at__month=hoje.month,
                ).count(),
                "ano": Appointment.objects.filter(scheduled_at__year=hoje.year).count(),
                "concluidas": qs.filter(status=AppointmentStatus.CONCLUIDA).count(),
                "canceladas": qs.filter(status=AppointmentStatus.CANCELADA).count(),
                "tempo_medio_minutos": tempo_minutos,
            },
            "por_medico": por_medico,
            "por_especialidade": [],
        }

    @staticmethod
    def relatorio_recepcao(filters: ReportFilters) -> dict:
        from apps.reception.models import ReceptionCheckIn, WaitingQueue

        ensure_filters(filters)
        start_dt, end_dt = datetime_range(filters)
        checkins = ReceptionCheckIn.objects.filter(check_in_time__range=(start_dt, end_dt))
        if filters.paciente_id:
            checkins = checkins.filter(patient_id=filters.paciente_id)
        if filters.estado:
            checkins = checkins.filter(status=filters.estado)

        fila = WaitingQueue.objects.filter(created_at__range=(start_dt, end_dt))
        tempo_medio = fila.aggregate(media=Avg("estimated_wait_minutes"))["media"] or 0
        fila_media = fila.count()
        por_prioridade = list(
            checkins.values("priority").annotate(total=Count("id")).order_by("-total")
        )

        return {
            "tipo": "recepcao",
            "periodo": filters.periodo,
            "data_inicio": filters.data_inicio.isoformat(),
            "data_fim": filters.data_fim.isoformat(),
            "resumo": {
                "check_ins": checkins.count(),
                "tempo_medio_espera_min": round(float(tempo_medio), 1),
                "fila_media": fila_media,
            },
            "por_prioridade": por_prioridade,
        }

    @staticmethod
    def relatorio_laboratorio(filters: ReportFilters) -> dict:
        from apps.laboratory.constants import PedidoLaboratorialEstado
        from apps.laboratory.models import PedidoLaboratorial, ResultadoLaboratorial

        ensure_filters(filters)
        start_dt, end_dt = datetime_range(filters)
        pedidos = PedidoLaboratorial.objects.filter(created_at__range=(start_dt, end_dt))
        if filters.paciente_id:
            pedidos = pedidos.filter(paciente_id=filters.paciente_id)
        if filters.estado:
            pedidos = pedidos.filter(estado=filters.estado)

        resultados = ResultadoLaboratorial.objects.filter(created_at__range=(start_dt, end_dt))

        return {
            "tipo": "laboratorio",
            "periodo": filters.periodo,
            "data_inicio": filters.data_inicio.isoformat(),
            "data_fim": filters.data_fim.isoformat(),
            "resumo": {
                "pedidos": pedidos.count(),
                "exames": pedidos.count(),
                "resultados": resultados.count(),
                "pendentes": pedidos.exclude(
                    estado__in=[PedidoLaboratorialEstado.CONCLUIDO, PedidoLaboratorialEstado.CANCELADO]
                ).count(),
                "concluidos": pedidos.filter(estado=PedidoLaboratorialEstado.CONCLUIDO).count(),
                "tempo_medio_horas": 0,
            },
        }

    @staticmethod
    def relatorio_faturacao(filters: ReportFilters) -> dict:
        from apps.billing.constants import PagamentoEstado
        from apps.billing.models import Fatura, ItemFatura, Orcamento, Pagamento, Recibo, Servico

        ensure_filters(filters)
        start_dt, end_dt = datetime_range(filters)
        faturas = Fatura.objects.filter(created_at__range=(start_dt, end_dt))
        pagamentos = Pagamento.objects.filter(created_at__range=(start_dt, end_dt))
        if filters.estado:
            pagamentos = pagamentos.filter(estado=filters.estado)

        servicos_vendidos = list(
            ItemFatura.objects.filter(fatura__created_at__range=(start_dt, end_dt))
            .values(nome=F("servico__nome"))
            .annotate(quantidade=Sum("quantidade"), total=Sum("subtotal"))
            .order_by("-quantidade")[:10]
        )

        return {
            "tipo": "faturacao",
            "periodo": filters.periodo,
            "data_inicio": filters.data_inicio.isoformat(),
            "data_fim": filters.data_fim.isoformat(),
            "resumo": {
                "faturas": faturas.count(),
                "pagamentos": pagamentos.count(),
                "pagamentos_confirmados": pagamentos.filter(estado=PagamentoEstado.CONFIRMADO).count(),
                "recibos": Recibo.objects.filter(created_at__range=(start_dt, end_dt)).count(),
                "orcamentos": Orcamento.objects.filter(created_at__range=(start_dt, end_dt)).count(),
                "servicos_catalogo": Servico.objects.filter(activo=True).count(),
            },
            "servicos_vendidos": servicos_vendidos,
        }

    @staticmethod
    def relatorio_financeiro(filters: ReportFilters) -> dict:
        from apps.finance.constants import DespesaEstado, MovimentoTipo
        from apps.finance.models import Despesa, MovimentoFinanceiro
        from apps.finance.services.finance_service import FinanceService

        ensure_filters(filters)
        start_dt, end_dt = datetime_range(filters)
        movimentos = MovimentoFinanceiro.objects.filter(data__range=(start_dt, end_dt))
        despesas = Despesa.objects.filter(data__range=(filters.data_inicio, filters.data_fim))
        if filters.categoria:
            despesas = despesas.filter(categoria=filters.categoria)

        entradas = movimentos.filter(tipo=MovimentoTipo.ENTRADA).aggregate(t=Sum("valor"))["t"] or 0
        saidas = movimentos.filter(tipo=MovimentoTipo.SAIDA).aggregate(t=Sum("valor"))["t"] or 0
        fluxo = FinanceService.calcular_fluxo_caixa()

        top_categorias = list(
            despesas.filter(estado=DespesaEstado.PAGA)
            .values("categoria")
            .annotate(total=Sum("valor"))
            .order_by("-total")[:10]
        )

        return {
            "tipo": "financeiro",
            "periodo": filters.periodo,
            "data_inicio": filters.data_inicio.isoformat(),
            "data_fim": filters.data_fim.isoformat(),
            "resumo": {
                "receitas": float(entradas),
                "despesas": float(saidas),
                "lucro": float(entradas) - float(saidas),
                "saldo_actual": fluxo.get("saldo_actual_caixas", 0),
            },
            "fluxo_caixa": fluxo,
            "top_categorias": [
                {"categoria": c["categoria"], "total": float(c["total"] or 0)} for c in top_categorias
            ],
        }

    @staticmethod
    def series_temporais() -> dict:
        cached_key = "all"
        from apps.reports.services.cache_service import ReportsCacheService

        cached = ReportsCacheService.get_charts(cached_key)
        if cached:
            return cached

        start = timezone.localdate() - timedelta(days=30)
        receitas = StatisticsService._serie_movimentos(start)
        consultas = StatisticsService._serie_consultas(start)
        pacientes = StatisticsService._serie_pacientes(start)
        laboratorio = StatisticsService._serie_laboratorio(start)
        pagamentos = StatisticsService._serie_pagamentos(start)

        data = {
            "receitas": receitas,
            "consultas": consultas,
            "pacientes": pacientes,
            "laboratorio": laboratorio,
            "pagamentos": pagamentos,
        }
        ReportsCacheService.set_charts(cached_key, data)
        return data

    @staticmethod
    def _serie_movimentos(start):
        from apps.finance.constants import MovimentoTipo
        from apps.finance.models import MovimentoFinanceiro

        rows = (
            MovimentoFinanceiro.objects.filter(
                data__date__gte=start,
                tipo=MovimentoTipo.ENTRADA,
            )
            .annotate(dia=TruncDate("data"))
            .values("dia")
            .annotate(total=Sum("valor"))
            .order_by("dia")
        )
        return [{"data": r["dia"].isoformat(), "valor": float(r["total"] or 0)} for r in rows]

    @staticmethod
    def _serie_consultas(start):
        from apps.appointments.models import Appointment

        rows = (
            Appointment.objects.filter(scheduled_at__date__gte=start)
            .annotate(dia=TruncDate("scheduled_at"))
            .values("dia")
            .annotate(total=Count("id"))
            .order_by("dia")
        )
        return [{"data": r["dia"].isoformat(), "valor": r["total"]} for r in rows]

    @staticmethod
    def _serie_pacientes(start):
        from apps.patients.models import Patient

        rows = (
            Patient.objects.filter(created_at__date__gte=start, deleted_at__isnull=True)
            .annotate(dia=TruncDate("created_at"))
            .values("dia")
            .annotate(total=Count("id"))
            .order_by("dia")
        )
        return [{"data": r["dia"].isoformat(), "valor": r["total"]} for r in rows]

    @staticmethod
    def _serie_laboratorio(start):
        from apps.laboratory.models import PedidoLaboratorial

        rows = (
            PedidoLaboratorial.objects.filter(created_at__date__gte=start)
            .annotate(dia=TruncDate("created_at"))
            .values("dia")
            .annotate(total=Count("id"))
            .order_by("dia")
        )
        return [{"data": r["dia"].isoformat(), "valor": r["total"]} for r in rows]

    @staticmethod
    def _serie_pagamentos(start):
        from apps.billing.constants import PagamentoEstado
        from apps.billing.models import Pagamento

        rows = (
            Pagamento.objects.filter(
                data_pagamento__date__gte=start,
                estado=PagamentoEstado.CONFIRMADO,
            )
            .annotate(dia=TruncDate("data_pagamento"))
            .values("dia")
            .annotate(total=Sum("valor"))
            .order_by("dia")
        )
        return [{"data": r["dia"].isoformat(), "valor": float(r["total"] or 0)} for r in rows]

    @staticmethod
    def serie_mensal_receitas():
        from apps.finance.constants import MovimentoTipo
        from apps.finance.models import MovimentoFinanceiro

        rows = (
            MovimentoFinanceiro.objects.filter(tipo=MovimentoTipo.ENTRADA)
            .annotate(mes=TruncMonth("data"))
            .values("mes")
            .annotate(total=Sum("valor"))
            .order_by("mes")[:12]
        )
        return [{"mes": r["mes"].strftime("%Y-%m"), "valor": float(r["total"] or 0)} for r in rows]
