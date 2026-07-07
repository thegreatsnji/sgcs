"""Serviço principal do módulo financeiro."""

from decimal import Decimal

from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

from apps.audit_logs.models import AuditAction
from apps.audit_logs.services import AuditService
from apps.finance.constants import (
    CaixaEstado,
    DEFAULT_CAIXA_CODIGO,
    DespesaEstado,
    MovimentoOrigem,
    MovimentoTipo,
)
from apps.finance.models import Caixa, CategoriaFinanceira, Despesa, MovimentoFinanceiro
from apps.finance.services.cache_service import FinanceCacheService
from core.events.event_bus import event_bus
from core.events.events import EventNames


class FinanceService:
    @staticmethod
    def _log(action, user, request, resource_type, resource_id, description, metadata=None):
        AuditService.log(
            action=action,
            user=user,
            request=request,
            description=description,
            resource_type=resource_type,
            resource_id=str(resource_id),
            metadata=metadata or {},
        )

    @staticmethod
    def _caixa_aberta() -> Caixa:
        caixa = Caixa.objects.filter(estado=CaixaEstado.ABERTO).order_by("id").first()
        if caixa:
            return caixa
        caixa, _ = Caixa.objects.get_or_create(
            codigo=DEFAULT_CAIXA_CODIGO,
            defaults={"nome": "Caixa Principal", "estado": CaixaEstado.FECHADO},
        )
        if caixa.estado != CaixaEstado.ABERTO:
            raise ValueError("Não existe caixa aberta. Abra um caixa antes de registar movimentos.")
        return caixa

    @staticmethod
    def _actualizar_saldo_caixa(caixa: Caixa, tipo: str, valor: Decimal) -> None:
        if tipo in {MovimentoTipo.ENTRADA, MovimentoTipo.AJUSTE}:
            caixa.saldo_actual += valor
        elif tipo in {MovimentoTipo.SAIDA, MovimentoTipo.TRANSFERENCIA}:
            caixa.saldo_actual -= valor
        caixa.save(update_fields=["saldo_actual", "updated_at"])

    @staticmethod
    @transaction.atomic
    def abrir_caixa(
        caixa_id: int,
        user,
        *,
        saldo_inicial: Decimal = Decimal("0.00"),
        observacoes: str = "",
        request=None,
    ) -> Caixa:
        caixa = Caixa.objects.select_for_update().get(pk=caixa_id)
        if caixa.estado == CaixaEstado.ABERTO:
            raise ValueError("O caixa já está aberto.")
        if Caixa.objects.filter(estado=CaixaEstado.ABERTO).exclude(pk=caixa_id).exists():
            raise ValueError("Já existe outro caixa aberto.")

        now = timezone.now()
        caixa.estado = CaixaEstado.ABERTO
        caixa.saldo_inicial = saldo_inicial
        caixa.saldo_actual = saldo_inicial
        caixa.data_abertura = now
        caixa.data_fecho = None
        caixa.utilizador_abertura = user
        caixa.utilizador_fecho = None
        caixa.observacoes = observacoes
        caixa.save()

        FinanceService._log(
            AuditAction.CAIXA_ABERTA,
            user,
            request,
            "finance_cash_register",
            caixa.pk,
            f"Caixa {caixa.codigo} aberta com saldo {saldo_inicial}.",
        )
        event_bus.publish(EventNames.FINANCE_CASH_OPENED, {"caixa_id": caixa.pk})
        FinanceCacheService.invalidate_all()
        return caixa

    @staticmethod
    @transaction.atomic
    def fechar_caixa(caixa_id: int, user, *, observacoes: str = "", request=None) -> Caixa:
        caixa = Caixa.objects.select_for_update().get(pk=caixa_id)
        if caixa.estado != CaixaEstado.ABERTO:
            raise ValueError("O caixa não está aberto.")

        caixa.estado = CaixaEstado.FECHADO
        caixa.data_fecho = timezone.now()
        caixa.utilizador_fecho = user
        if observacoes:
            caixa.observacoes = observacoes
        caixa.save()

        FinanceService._log(
            AuditAction.CAIXA_FECHADA,
            user,
            request,
            "finance_cash_register",
            caixa.pk,
            f"Caixa {caixa.codigo} fechada. Saldo final: {caixa.saldo_actual}.",
        )
        event_bus.publish(EventNames.FINANCE_CASH_CLOSED, {"caixa_id": caixa.pk})

        from apps.finance.tasks import fechar_caixa as fechar_caixa_task

        fechar_caixa_task.delay(caixa.pk)
        FinanceCacheService.invalidate_all()
        return caixa

    @staticmethod
    @transaction.atomic
    def criar_movimento(
        user,
        *,
        caixa_id: int | None = None,
        tipo: str,
        origem: str,
        valor: Decimal,
        descricao: str,
        referencia: str = "",
        pagamento_id: int | None = None,
        despesa_id: int | None = None,
        request=None,
    ) -> MovimentoFinanceiro:
        caixa = (
            Caixa.objects.select_for_update().get(pk=caixa_id)
            if caixa_id
            else FinanceService._caixa_aberta()
        )
        if caixa.estado != CaixaEstado.ABERTO:
            raise ValueError("O caixa deve estar aberto para movimentos.")

        movimento = MovimentoFinanceiro.objects.create(
            caixa=caixa,
            tipo=tipo,
            origem=origem,
            valor=valor,
            descricao=descricao,
            referencia=referencia,
            pagamento_id=pagamento_id,
            despesa_id=despesa_id,
            utilizador=user,
            data=timezone.now(),
        )
        FinanceService._actualizar_saldo_caixa(caixa, tipo, valor)

        FinanceService._log(
            AuditAction.MOVIMENTO_FINANCEIRO,
            user,
            request,
            "finance_movement",
            movimento.pk,
            f"Movimento {tipo} de {valor} registado.",
            {"caixa_id": caixa.pk},
        )
        FinanceCacheService.invalidate_all()
        return movimento

    @staticmethod
    @transaction.atomic
    def processar_pagamento_billing(pagamento_id: int, user, request=None) -> MovimentoFinanceiro | None:
        from apps.billing.models import Pagamento

        if MovimentoFinanceiro.objects.filter(pagamento_id=pagamento_id).exists():
            return None

        pagamento = Pagamento.objects.select_related("fatura").get(pk=pagamento_id)
        try:
            caixa = FinanceService._caixa_aberta()
        except ValueError:
            caixa, created = Caixa.objects.get_or_create(
                codigo=DEFAULT_CAIXA_CODIGO,
                defaults={"nome": "Caixa Principal"},
            )
            if created or caixa.estado != CaixaEstado.ABERTO:
                FinanceService.abrir_caixa(
                    caixa.pk,
                    user,
                    saldo_inicial=Decimal("0.00"),
                    observacoes="Abertura automática para recepção de pagamentos.",
                    request=request,
                )
                caixa.refresh_from_db()

        movimento = FinanceService.criar_movimento(
            user,
            caixa_id=caixa.pk,
            tipo=MovimentoTipo.ENTRADA,
            origem=MovimentoOrigem.PAGAMENTO,
            valor=pagamento.valor,
            descricao=f"Pagamento fatura {pagamento.fatura.numero}",
            referencia=pagamento.referencia or str(pagamento.pk),
            pagamento_id=pagamento.pk,
            request=request,
        )
        event_bus.publish(
            EventNames.FINANCE_PAYMENT_RECEIVED,
            {
                "pagamento_id": pagamento.pk,
                "movimento_id": movimento.pk,
                "valor": str(pagamento.valor),
            },
        )
        FinanceCacheService.invalidate_all()
        return movimento

    @staticmethod
    @transaction.atomic
    def criar_despesa(user, data: dict, request=None) -> Despesa:
        despesa = Despesa.objects.create(
            fornecedor=data["fornecedor"],
            categoria=data.get("categoria", "OUTROS"),
            categoria_financeira_id=data.get("categoria_financeira"),
            valor=data["valor"],
            descricao=data["descricao"],
            data=data["data"],
            observacoes=data.get("observacoes", ""),
            criado_por=user,
        )
        FinanceService._log(
            AuditAction.DESPESA_CRIADA,
            user,
            request,
            "finance_expense",
            despesa.pk,
            f"Despesa criada — {despesa.fornecedor}.",
        )
        event_bus.publish(EventNames.FINANCE_EXPENSE_CREATED, {"despesa_id": despesa.pk})
        FinanceCacheService.invalidate_all()
        return despesa

    @staticmethod
    @transaction.atomic
    def aprovar_despesa(despesa_id: int, user, request=None) -> Despesa:
        despesa = Despesa.objects.select_for_update().get(pk=despesa_id)
        if despesa.estado != DespesaEstado.PENDENTE:
            raise ValueError("Apenas despesas pendentes podem ser aprovadas.")
        despesa.estado = DespesaEstado.APROVADA
        despesa.save(update_fields=["estado", "updated_at"])
        FinanceService._log(
            AuditAction.DESPESA_APROVADA,
            user,
            request,
            "finance_expense",
            despesa.pk,
            f"Despesa aprovada — {despesa.fornecedor}.",
        )
        FinanceCacheService.invalidate_all()
        return despesa

    @staticmethod
    @transaction.atomic
    def pagar_despesa(despesa_id: int, user, request=None) -> Despesa:
        despesa = Despesa.objects.select_for_update().get(pk=despesa_id)
        if despesa.estado != DespesaEstado.APROVADA:
            raise ValueError("A despesa deve estar aprovada para pagamento.")
        despesa.estado = DespesaEstado.PAGA
        despesa.save(update_fields=["estado", "updated_at"])

        FinanceService.criar_movimento(
            user,
            tipo=MovimentoTipo.SAIDA,
            origem=MovimentoOrigem.DESPESA,
            valor=despesa.valor,
            descricao=f"Despesa — {despesa.fornecedor}",
            referencia=str(despesa.pk),
            despesa_id=despesa.pk,
            request=request,
        )
        FinanceService._log(
            AuditAction.DESPESA_PAGA,
            user,
            request,
            "finance_expense",
            despesa.pk,
            f"Despesa paga — {despesa.fornecedor}.",
        )
        FinanceCacheService.invalidate_all()
        return despesa

    @staticmethod
    def calcular_fluxo_caixa() -> dict:
        today = timezone.localdate()
        month_start = today.replace(day=1)

        entradas_hoje = MovimentoFinanceiro.objects.filter(
            tipo=MovimentoTipo.ENTRADA, data__date=today
        ).aggregate(s=Sum("valor"))["s"] or Decimal("0.00")
        saidas_hoje = MovimentoFinanceiro.objects.filter(
            tipo=MovimentoTipo.SAIDA, data__date=today
        ).aggregate(s=Sum("valor"))["s"] or Decimal("0.00")

        entradas_mes = MovimentoFinanceiro.objects.filter(
            tipo=MovimentoTipo.ENTRADA, data__date__gte=month_start
        ).aggregate(s=Sum("valor"))["s"] or Decimal("0.00")
        saidas_mes = MovimentoFinanceiro.objects.filter(
            tipo=MovimentoTipo.SAIDA, data__date__gte=month_start
        ).aggregate(s=Sum("valor"))["s"] or Decimal("0.00")

        saldo_caixas = Caixa.objects.filter(estado=CaixaEstado.ABERTO).aggregate(
            s=Sum("saldo_actual")
        )["s"] or Decimal("0.00")

        return {
            "receitas_hoje": float(entradas_hoje),
            "receitas_mes": float(entradas_mes),
            "despesas_hoje": float(saidas_hoje),
            "despesas_mes": float(saidas_mes),
            "saldo_diario": float(entradas_hoje - saidas_hoje),
            "saldo_mensal": float(entradas_mes - saidas_mes),
            "saldo_actual_caixas": float(saldo_caixas),
            "fluxo_diario": {"entradas": float(entradas_hoje), "saidas": float(saidas_hoje)},
            "fluxo_mensal": {"entradas": float(entradas_mes), "saidas": float(saidas_mes)},
        }

    @staticmethod
    def get_dashboard_summary() -> dict:
        cached = FinanceCacheService.get_dashboard()
        if cached:
            return cached

        fluxo = FinanceService.calcular_fluxo_caixa()
        from apps.billing.constants import PagamentoEstado
        from apps.billing.models import Pagamento

        today = timezone.localdate()
        pagamentos_confirmados = Pagamento.objects.filter(estado=PagamentoEstado.CONFIRMADO).count()
        pagamentos_hoje = Pagamento.objects.filter(
            estado=PagamentoEstado.CONFIRMADO, data_pagamento__date=today
        ).count()

        from django.db.models import Count

        top_categorias = list(
            Despesa.objects.filter(estado=DespesaEstado.PAGA)
            .values("categoria")
            .annotate(total=Sum("valor"))
            .order_by("-total")[:5]
        )

        servicos_top = []
        try:
            from apps.billing.models import ItemFatura

            servicos_top = list(
                ItemFatura.objects.values("servico__nome")
                .annotate(total=Sum("quantidade"))
                .order_by("-total")[:5]
            )
        except Exception:
            pass

        data = {
            "indicadores": {
                "receita_hoje": fluxo["receitas_hoje"],
                "receita_mensal": fluxo["receitas_mes"],
                "despesa_hoje": fluxo["despesas_hoje"],
                "despesa_mensal": fluxo["despesas_mes"],
                "lucro": fluxo["saldo_mensal"],
                "saldo_actual": fluxo["saldo_actual_caixas"],
                "pagamentos_confirmados": pagamentos_confirmados,
                "pagamentos_hoje": pagamentos_hoje,
            },
            "fluxo_caixa": fluxo,
            "top_categorias": [
                {"categoria": c["categoria"], "total": float(c["total"] or 0)} for c in top_categorias
            ],
            "servicos_mais_vendidos": [
                {"servico": s["servico__nome"], "quantidade": s["total"] or 0} for s in servicos_top
            ],
        }
        FinanceCacheService.set_dashboard(data)
        return data

    @staticmethod
    def gerar_relatorio(tipo: str, request=None) -> dict:
        now = timezone.localdate()
        if tipo == "daily":
            periodo = now.isoformat()
            inicio = now
            fim = now
        elif tipo == "monthly":
            periodo = f"{now.year}-{now.month:02d}"
            inicio = now.replace(day=1)
            fim = now
        else:
            periodo = str(now.year)
            inicio = now.replace(month=1, day=1)
            fim = now

        cached = FinanceCacheService.get_report(tipo, periodo)
        if cached:
            return cached

        entradas = MovimentoFinanceiro.objects.filter(
            tipo=MovimentoTipo.ENTRADA, data__date__gte=inicio, data__date__lte=fim
        ).aggregate(s=Sum("valor"))["s"] or Decimal("0.00")
        saidas = MovimentoFinanceiro.objects.filter(
            tipo=MovimentoTipo.SAIDA, data__date__gte=inicio, data__date__lte=fim
        ).aggregate(s=Sum("valor"))["s"] or Decimal("0.00")

        from apps.billing.constants import PagamentoEstado
        from apps.billing.models import ItemFatura, Pagamento

        pagamentos = Pagamento.objects.filter(
            estado=PagamentoEstado.CONFIRMADO,
            data_pagamento__date__gte=inicio,
            data_pagamento__date__lte=fim,
        ).count()

        servicos = list(
            ItemFatura.objects.filter(fatura__emitida_em__date__gte=inicio, fatura__emitida_em__date__lte=fim)
            .values("servico__nome")
            .annotate(total=Sum("quantidade"))
            .order_by("-total")[:10]
        )

        data = {
            "tipo": tipo,
            "periodo": periodo,
            "receitas": float(entradas),
            "despesas": float(saidas),
            "lucro": float(entradas - saidas),
            "fluxo_caixa": {"entradas": float(entradas), "saidas": float(saidas)},
            "pagamentos": pagamentos,
            "servicos_mais_vendidos": [
                {"servico": s["servico__nome"], "quantidade": s["total"] or 0} for s in servicos
            ],
        }

        FinanceService._log(
            AuditAction.RELATORIO_FINANCEIRO,
            None,
            request,
            "finance_report",
            periodo,
            f"Relatório {tipo} gerado.",
            {"tipo": tipo},
        )
        event_bus.publish(EventNames.FINANCE_REPORT_GENERATED, {"tipo": tipo, "periodo": periodo})
        FinanceCacheService.set_report(tipo, periodo, data)

        from apps.finance.tasks import gerar_relatorio_pdf

        gerar_relatorio_pdf.delay(tipo, periodo)
        return data

    @staticmethod
    def historico_caixa(caixa_id: int) -> dict:
        caixa = Caixa.objects.get(pk=caixa_id)
        movimentos = MovimentoFinanceiro.objects.filter(caixa=caixa).order_by("-data")[:100]
        return {
            "caixa": {
                "id": caixa.pk,
                "codigo": caixa.codigo,
                "nome": caixa.nome,
                "estado": caixa.estado,
                "saldo_actual": str(caixa.saldo_actual),
            },
            "movimentos": [
                {
                    "id": m.pk,
                    "tipo": m.tipo,
                    "origem": m.origem,
                    "valor": str(m.valor),
                    "descricao": m.descricao,
                    "data": m.data.isoformat(),
                }
                for m in movimentos
            ],
        }
