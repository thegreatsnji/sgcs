"""Resumo financeiro operacional do balcão (Receção).

Agrega apenas Fatura / Pagamento / ItemFatura do SGCS.
Não consulta PatientHistory nem movimentos financeiros administrativos.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from django.db.models import Case, DecimalField, F, Q, Sum, Value, When
from django.db.models.functions import Coalesce

from apps.billing.constants import FaturaEstado, PagamentoEstado
from apps.billing.models import Fatura, ItemFatura, Pagamento
from apps.billing.period import datetime_bounds


def _d(value) -> Decimal:
    if value is None:
        return Decimal("0.00")
    return Decimal(value).quantize(Decimal("0.01"))


def get_resumo_operacional(*, data_inicio: date, data_fim: date) -> dict:
    """Métricas do balcão para [data_inicio, data_fim] inclusivo.

    - total_faturado: SUM(Fatura.total) emitidas no período, excl. CANCELADA
    - total_recebido: SUM(Pagamento.valor) CONFIRMADO com data_pagamento no período
    - saldo_pendente: SUM(max(total - pago_confirmado, 0)) das faturas emitidas no período
    - total_reducoes: SUM(ItemFatura.valor_reducao) em faturas emitidas no período (não canceladas)
    - numero_pagamentos: COUNT pagamentos confirmados no período
    """
    start_dt, end_dt = datetime_bounds(data_inicio, data_fim)
    zero = Value(Decimal("0.00"), output_field=DecimalField(max_digits=14, decimal_places=2))

    faturas_periodo = Fatura.objects.filter(
        emitida_em__gte=start_dt,
        emitida_em__lte=end_dt,
    ).exclude(estado=FaturaEstado.CANCELADA)

    total_faturado = _d(faturas_periodo.aggregate(s=Sum("total"))["s"])

    pagamentos_periodo = Pagamento.objects.filter(
        estado=PagamentoEstado.CONFIRMADO,
        data_pagamento__gte=start_dt,
        data_pagamento__lte=end_dt,
    )
    total_recebido = _d(pagamentos_periodo.aggregate(s=Sum("valor"))["s"])
    numero_pagamentos = pagamentos_periodo.count()

    faturas_com_pago = faturas_periodo.annotate(
        pago=Coalesce(
            Sum(
                "pagamentos__valor",
                filter=Q(pagamentos__estado=PagamentoEstado.CONFIRMADO),
            ),
            zero,
        )
    )
    saldo_pendente = _d(
        faturas_com_pago.aggregate(
            s=Sum(
                Case(
                    When(total__gt=F("pago"), then=F("total") - F("pago")),
                    default=zero,
                    output_field=DecimalField(max_digits=14, decimal_places=2),
                )
            )
        )["s"]
    )

    total_reducoes = _d(
        ItemFatura.objects.filter(
            valor_reducao__gt=0,
            fatura__emitida_em__gte=start_dt,
            fatura__emitida_em__lte=end_dt,
        )
        .exclude(fatura__estado=FaturaEstado.CANCELADA)
        .aggregate(s=Sum("valor_reducao"))["s"]
    )

    return {
        "periodo": {
            "data_inicio": data_inicio.isoformat(),
            "data_fim": data_fim.isoformat(),
        },
        "total_faturado": str(total_faturado),
        "total_recebido": str(total_recebido),
        "saldo_pendente": str(saldo_pendente),
        "total_reducoes": str(total_reducoes),
        "numero_pagamentos": numero_pagamentos,
    }
