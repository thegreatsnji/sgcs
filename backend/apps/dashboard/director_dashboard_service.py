"""Dashboard executivo do Director — agregados sem permissões de Receção."""

from __future__ import annotations

import logging
from datetime import date, timedelta
from decimal import Decimal

from django.db.models import F, Q, Sum, Value
from django.db.models import DecimalField
from django.db.models.functions import Coalesce

from apps.billing.constants import FaturaEstado, PagamentoEstado
from apps.billing.models import Fatura, ItemFatura
from apps.billing.period import datetime_bounds
from apps.billing.services.resumo_operacional import get_resumo_operacional

logger = logging.getLogger(__name__)


def _section_ok(data: dict) -> dict:
    return {"ok": True, "data": data}


def _section_error(message: str = "Não foi possível carregar este indicador.") -> dict:
    return {"ok": False, "error": message}


class DirectorDashboardService:
    @staticmethod
    def get_summary(*, data_inicio: date, data_fim: date) -> dict:
        """Agrega métricas do Director. Cada secção isola falhas."""
        return {
            "periodo": {
                "data_inicio": data_inicio.isoformat(),
                "data_fim": data_fim.isoformat(),
            },
            "financeiro": DirectorDashboardService._financeiro(data_inicio, data_fim),
            "operacional": DirectorDashboardService._operacional(data_inicio, data_fim),
            "laboratorio": DirectorDashboardService._laboratorio(data_inicio, data_fim),
            "stock": DirectorDashboardService._stock(),
            "servicos_faturados": DirectorDashboardService._servicos_faturados(
                data_inicio, data_fim
            ),
        }

    @staticmethod
    def _financeiro(data_inicio: date, data_fim: date) -> dict:
        try:
            resumo = get_resumo_operacional(data_inicio=data_inicio, data_fim=data_fim)
            start_dt, end_dt = datetime_bounds(data_inicio, data_fim)
            zero = Value(Decimal("0.00"), output_field=DecimalField(max_digits=14, decimal_places=2))
            faturas = (
                Fatura.objects.filter(emitida_em__gte=start_dt, emitida_em__lte=end_dt)
                .exclude(estado=FaturaEstado.CANCELADA)
                .annotate(
                    pago=Coalesce(
                        Sum(
                            "pagamentos__valor",
                            filter=Q(pagamentos__estado=PagamentoEstado.CONFIRMADO),
                        ),
                        zero,
                    )
                )
            )
            faturas_com_saldo = faturas.filter(total__gt=F("pago")).count()
            return _section_ok(
                {
                    "total_faturado": resumo["total_faturado"],
                    "total_recebido": resumo["total_recebido"],
                    "saldo_pendente": resumo["saldo_pendente"],
                    "total_reducoes": resumo["total_reducoes"],
                    "numero_pagamentos": resumo["numero_pagamentos"],
                    "faturas_com_saldo": faturas_com_saldo,
                    "semantica": {
                        "faturado": "emitida_em",
                        "recebido": "data_pagamento",
                        "saldo": "aberto_faturas_periodo",
                    },
                }
            )
        except Exception:
            logger.exception("Director dashboard: falha financeiro")
            return _section_error()

    @staticmethod
    def _operacional(data_inicio: date, data_fim: date) -> dict:
        try:
            from apps.appointments.constants import AppointmentStatus
            from apps.appointments.models import Appointment
            from apps.reception.constants import CheckInStatus
            from apps.reception.models import ReceptionCheckIn

            start_dt, end_dt = datetime_bounds(data_inicio, data_fim)

            utentes_atendidos = ReceptionCheckIn.objects.filter(
                status=CheckInStatus.COMPLETED,
                check_in_time__gte=start_dt,
                check_in_time__lte=end_dt,
            ).count()

            consultas_qs = Appointment.objects.filter(
                consultation_date__gte=data_inicio,
                consultation_date__lte=data_fim,
            )
            consultas = consultas_qs.count()
            consultas_concluidas = consultas_qs.filter(
                status=AppointmentStatus.CONCLUIDA
            ).count()
            consultas_em_espera = Appointment.objects.filter(
                status__in=[AppointmentStatus.CONFIRMADA, AppointmentStatus.EM_ESPERA]
            ).count()

            return _section_ok(
                {
                    "utentes_atendidos": utentes_atendidos,
                    "utentes_atendidos_definicao": "check_ins_concluidos",
                    "consultas": consultas,
                    "consultas_concluidas": consultas_concluidas,
                    "consultas_em_espera": consultas_em_espera,
                }
            )
        except Exception:
            logger.exception("Director dashboard: falha operacional")
            return _section_error()

    @staticmethod
    def _laboratorio(data_inicio: date, data_fim: date) -> dict:
        try:
            from apps.appointments.constants import PedidoLaboratorioEstadoFaturacao
            from apps.laboratory.constants import (
                PENDING_STATUSES,
                PedidoLaboratorialEstado,
                ResultadoLaboratorialEstado,
            )
            from apps.laboratory.models import PedidoLaboratorial, ResultadoLaboratorial

            start_dt, end_dt = datetime_bounds(data_inicio, data_fim)

            pedidos_pendentes = PedidoLaboratorial.objects.filter(
                estado__in=PENDING_STATUSES
            ).count()
            aguardam_regularizacao = (
                PedidoLaboratorial.objects.filter(
                    pedido_consulta__estado_faturacao=(
                        PedidoLaboratorioEstadoFaturacao.AGUARDA_REGULARIZACAO
                    )
                )
                .exclude(estado=PedidoLaboratorialEstado.CANCELADO)
                .count()
            )
            aguardam_validacao = ResultadoLaboratorial.objects.filter(
                estado__in=[
                    ResultadoLaboratorialEstado.EM_PROCESSAMENTO,
                    ResultadoLaboratorialEstado.RESULTADO_PENDENTE,
                ]
            ).count()
            concluidos_periodo = PedidoLaboratorial.objects.filter(
                estado=PedidoLaboratorialEstado.CONCLUIDO,
                data_conclusao__gte=start_dt,
                data_conclusao__lte=end_dt,
            ).count()

            return _section_ok(
                {
                    "pedidos_pendentes": pedidos_pendentes,
                    "aguardam_regularizacao": aguardam_regularizacao,
                    "aguardam_validacao": aguardam_validacao,
                    "concluidos_periodo": concluidos_periodo,
                }
            )
        except Exception:
            logger.exception("Director dashboard: falha laboratorio")
            return _section_error()

    @staticmethod
    def _stock() -> dict:
        try:
            from apps.pharmacy.models import MedicamentoUrgencia
            from apps.pharmacy.status import dias_proxima_validade

            qs = MedicamentoUrgencia.objects.filter(activo=True)
            hoje = date.today()
            limite = hoje + timedelta(days=dias_proxima_validade())
            expirado = qs.filter(validade__lt=hoje)
            sem = qs.filter(quantidade_stock=0).filter(
                Q(validade__isnull=True) | Q(validade__gte=hoje)
            )
            proximo = qs.filter(
                quantidade_stock__gt=0, validade__gte=hoje, validade__lte=limite
            )
            baixo = qs.filter(
                quantidade_stock__gt=0, quantidade_stock__lte=F("stock_minimo")
            ).filter(Q(validade__isnull=True) | Q(validade__gt=limite))

            return _section_ok(
                {
                    "stock_baixo": baixo.count(),
                    "sem_stock": sem.count(),
                    "proximos_validade": proximo.count(),
                    "expirados": expirado.count(),
                }
            )
        except Exception:
            logger.exception("Director dashboard: falha stock")
            return _section_error()

    @staticmethod
    def _servicos_faturados(data_inicio: date, data_fim: date) -> dict:
        """Linhas de fatura no período (quantidade). Não exige pagamento."""
        try:
            start_dt, end_dt = datetime_bounds(data_inicio, data_fim)
            rows = list(
                ItemFatura.objects.filter(
                    fatura__emitida_em__gte=start_dt,
                    fatura__emitida_em__lte=end_dt,
                )
                .exclude(fatura__estado=FaturaEstado.CANCELADA)
                .values("servico__nome")
                .annotate(quantidade=Sum("quantidade"))
                .order_by("-quantidade")[:6]
            )
            return _section_ok(
                {
                    "itens": [
                        {
                            "servico": r["servico__nome"] or "—",
                            "quantidade": int(r["quantidade"] or 0),
                        }
                        for r in rows
                    ],
                    "semantica": "linhas_fatura_periodo",
                }
            )
        except Exception:
            logger.exception("Director dashboard: falha servicos")
            return _section_error()
