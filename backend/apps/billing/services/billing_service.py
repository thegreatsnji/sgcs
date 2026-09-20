"""Serviço principal de faturação."""

from decimal import Decimal

from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

from apps.audit_logs.models import AuditAction
from apps.audit_logs.services import AuditService
from apps.billing.constants import (
    DEFAULT_TAX_RATE,
    FaturaEstado,
    OrcamentoEstado,
    PagamentoEstado,
)
from apps.billing.models import (
    Fatura,
    ItemFatura,
    ItemOrcamento,
    Orcamento,
    Pagamento,
    Recibo,
    Servico,
)
from apps.billing.services.cache_service import BillingCacheService
from apps.billing.services.number_service import BillingNumberService
from apps.billing.validators import validate_consulta_sem_fatura, validate_fatura_editavel
from core.events.event_bus import event_bus
from core.events.events import EventNames


class BillingService:
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
    def _calcular_totais(subtotal: Decimal, desconto: Decimal) -> tuple[Decimal, Decimal, Decimal]:
        desconto = max(desconto, Decimal("0.00"))
        base = max(subtotal - desconto, Decimal("0.00"))
        imposto = (base * DEFAULT_TAX_RATE).quantize(Decimal("0.01"))
        total = base + imposto
        return subtotal, imposto, total

    @staticmethod
    def _recalcular_orcamento(orcamento: Orcamento) -> None:
        subtotal = (
            orcamento.itens.aggregate(total=Sum("subtotal"))["total"] or Decimal("0.00")
        )
        subtotal, imposto, total = BillingService._calcular_totais(subtotal, orcamento.desconto)
        orcamento.subtotal = subtotal
        orcamento.imposto = imposto
        orcamento.total = total
        orcamento.save(update_fields=["subtotal", "imposto", "total", "updated_at"])

    @staticmethod
    def _recalcular_fatura(fatura: Fatura) -> None:
        subtotal = (
            fatura.itens.aggregate(total=Sum("subtotal"))["total"] or Decimal("0.00")
        )
        subtotal, imposto, total = BillingService._calcular_totais(subtotal, fatura.desconto)
        fatura.subtotal = subtotal
        fatura.imposto = imposto
        fatura.total = total
        fatura.save(update_fields=["subtotal", "imposto", "total", "updated_at"])

    @staticmethod
    def _actualizar_estado_fatura(fatura: Fatura) -> None:
        total_pago = (
            fatura.pagamentos.filter(estado=PagamentoEstado.CONFIRMADO).aggregate(
                s=Sum("valor")
            )["s"]
            or Decimal("0.00")
        )
        if fatura.estado == FaturaEstado.CANCELADA:
            return
        if total_pago >= fatura.total and fatura.total > 0:
            fatura.estado = FaturaEstado.PAGA
        elif total_pago > 0:
            fatura.estado = FaturaEstado.PARCIAL
        else:
            fatura.estado = FaturaEstado.PENDENTE
        fatura.save(update_fields=["estado", "updated_at"])

    @staticmethod
    @transaction.atomic
    def criar_orcamento(
        paciente_id: int,
        user,
        *,
        validade=None,
        desconto: Decimal = Decimal("0.00"),
        itens: list[dict] | None = None,
        request=None,
    ) -> Orcamento:
        orcamento = Orcamento.objects.create(
            numero=BillingNumberService.generate_quote(),
            paciente_id=paciente_id,
            criado_por=user,
            estado=OrcamentoEstado.RASCUNHO,
            desconto=desconto,
            validade=validade,
        )
        for item in itens or []:
            BillingService.adicionar_item_orcamento(
                orcamento.pk,
                user,
                item,
                request=request,
                recalcular=False,
            )
        BillingService._recalcular_orcamento(orcamento)
        orcamento.refresh_from_db()

        BillingService._log(
            AuditAction.ORCAMENTO_CRIADO,
            user,
            request,
            "billing_quote",
            orcamento.pk,
            f"Orçamento {orcamento.numero} criado.",
            {"paciente_id": paciente_id},
        )
        event_bus.publish(
            EventNames.BILLING_QUOTE_CREATED,
            {"orcamento_id": orcamento.pk, "paciente_id": paciente_id},
        )
        BillingCacheService.invalidate_all(patient_id=paciente_id)
        return orcamento

    @staticmethod
    @transaction.atomic
    def adicionar_item_orcamento(
        orcamento_id: int,
        user,
        data: dict,
        *,
        request=None,
        recalcular: bool = True,
    ) -> ItemOrcamento:
        orcamento = Orcamento.objects.select_for_update().get(pk=orcamento_id)
        if not orcamento.is_editavel:
            raise ValueError("Não é possível alterar um orçamento aprovado ou expirado.")

        servico = Servico.objects.get(pk=data["servico_id"], activo=True)
        from apps.billing.services.catalog_service import assert_servico_faturavel

        assert_servico_faturavel(servico, user)
        quantidade = int(data.get("quantidade", 1))
        preco_raw = data.get("preco_unitario")
        preco_unitario = Decimal(str(preco_raw)) if preco_raw is not None else servico.preco
        subtotal = (preco_unitario * quantidade).quantize(Decimal("0.01"))

        item = ItemOrcamento.objects.create(
            orcamento=orcamento,
            servico=servico,
            quantidade=quantidade,
            preco_unitario=preco_unitario,
            subtotal=subtotal,
        )
        if recalcular:
            BillingService._recalcular_orcamento(orcamento)
            BillingCacheService.invalidate_all(patient_id=orcamento.paciente_id)
        return item

    @staticmethod
    @transaction.atomic
    def aprovar_orcamento(orcamento_id: int, user, request=None) -> Orcamento:
        orcamento = Orcamento.objects.select_for_update().get(pk=orcamento_id)
        if orcamento.estado not in {OrcamentoEstado.RASCUNHO, OrcamentoEstado.PENDENTE}:
            raise ValueError("Apenas orçamentos em rascunho ou pendentes podem ser aprovados.")
        if not orcamento.itens.exists():
            raise ValueError("O orçamento deve ter pelo menos um item.")

        orcamento.estado = OrcamentoEstado.APROVADO
        orcamento.save(update_fields=["estado", "updated_at"])

        BillingService._log(
            AuditAction.ORCAMENTO_APROVADO,
            user,
            request,
            "billing_quote",
            orcamento.pk,
            f"Orçamento {orcamento.numero} aprovado.",
        )
        BillingCacheService.invalidate_all(patient_id=orcamento.paciente_id)
        return orcamento

    @staticmethod
    @transaction.atomic
    def gerar_fatura(
        user,
        *,
        paciente_id: int | None = None,
        consulta_id: int | None = None,
        orcamento_id: int | None = None,
        desconto: Decimal | None = None,
        itens: list[dict] | None = None,
        request=None,
    ) -> Fatura:
        validate_consulta_sem_fatura(consulta_id)

        orcamento = None
        if orcamento_id:
            orcamento = Orcamento.objects.select_related("paciente").get(pk=orcamento_id)
            if orcamento.estado != OrcamentoEstado.APROVADO:
                raise ValueError("Apenas orçamentos aprovados podem gerar fatura.")
            paciente_id = orcamento.paciente_id
            desconto = desconto if desconto is not None else orcamento.desconto
        elif not paciente_id:
            raise ValueError("Indique o paciente ou um orçamento aprovado.")

        now = timezone.now()
        fatura = Fatura.objects.create(
            numero=BillingNumberService.generate_invoice(),
            paciente_id=paciente_id,
            consulta_id=consulta_id,
            orcamento=orcamento,
            estado=FaturaEstado.PENDENTE,
            desconto=desconto or Decimal("0.00"),
            emitida_em=now,
            emitida_por=user,
        )

        if orcamento:
            for item in orcamento.itens.select_related("servico"):
                BillingService.adicionar_item_fatura(
                    fatura.pk,
                    user,
                    {
                        "servico_id": item.servico_id,
                        "quantidade": item.quantidade,
                        "preco": item.preco_unitario,
                    },
                    request=request,
                    recalcular=False,
                )
        else:
            for item in itens or []:
                BillingService.adicionar_item_fatura(
                    fatura.pk,
                    user,
                    item,
                    request=request,
                    recalcular=False,
                )

        BillingService._recalcular_fatura(fatura)
        fatura.refresh_from_db()

        BillingService._log(
            AuditAction.FACTURA_CRIADA,
            user,
            request,
            "billing_invoice",
            fatura.pk,
            f"Fatura {fatura.numero} criada.",
            {"paciente_id": paciente_id, "consulta_id": consulta_id},
        )
        event_bus.publish(
            EventNames.BILLING_INVOICE_CREATED,
            {
                "fatura_id": fatura.pk,
                "paciente_id": paciente_id,
                "consulta_id": consulta_id,
            },
        )
        BillingCacheService.invalidate_all(patient_id=paciente_id)
        return fatura

    @staticmethod
    @transaction.atomic
    def adicionar_item_fatura(
        fatura_id: int,
        user,
        data: dict,
        *,
        request=None,
        recalcular: bool = True,
    ) -> ItemFatura:
        fatura = Fatura.objects.select_for_update().get(pk=fatura_id)
        validate_fatura_editavel(fatura)

        servico = Servico.objects.get(pk=data["servico_id"], activo=True)
        from apps.billing.services.catalog_service import assert_servico_faturavel

        assert_servico_faturavel(servico, user)
        quantidade = int(data.get("quantidade", 1))
        from apps.billing.services.reduction_service import ReductionError, resolve_item_pricing

        preco_cobrado_raw = data.get("preco_cobrado", data.get("preco"))
        try:
            pricing = resolve_item_pricing(
                servico,
                user,
                quantidade=quantidade,
                preco_cobrado_raw=preco_cobrado_raw,
                motivo_reducao=data.get("motivo_reducao"),
                observacao_reducao=data.get("observacao_reducao"),
                autorizacao_reducao_id=data.get("autorizacao_reducao_id"),
                request=request,
            )
        except ReductionError as exc:
            raise ValueError(str(exc)) from exc

        item = ItemFatura.objects.create(
            fatura=fatura,
            servico=servico,
            quantidade=quantidade,
            **pricing,
        )
        if pricing["valor_reducao"] > 0:
            BillingService._log(
                AuditAction.REDUCAO_VALOR_APLICADA,
                user,
                request,
                "billing_invoice_item",
                item.pk,
                f"Redução aplicada em {servico.nome}.",
                {
                    "fatura_id": fatura.pk,
                    "preco_oficial": str(pricing["preco_oficial"]),
                    "preco_cobrado": str(pricing["preco"]),
                    "valor_reducao": str(pricing["valor_reducao"]),
                    "motivo": pricing["motivo_reducao"],
                },
            )
            auth = pricing.get("autorizacao_reducao")
            if auth and not auth.fatura_id:
                auth.fatura = fatura
                auth.save(update_fields=["fatura", "updated_at"])
        if recalcular:
            BillingService._recalcular_fatura(fatura)
            BillingCacheService.invalidate_all(patient_id=fatura.paciente_id)
        return item

    @staticmethod
    def _comprometido_pagamentos(fatura: Fatura, *, exclude_pagamento_id: int | None = None) -> Decimal:
        """Soma valores que ocupam saldo: confirmados, pendentes e processados."""
        qs = fatura.pagamentos.filter(
            estado__in={
                PagamentoEstado.PENDENTE,
                PagamentoEstado.PROCESSADO,
                PagamentoEstado.CONFIRMADO,
            }
        )
        if exclude_pagamento_id:
            qs = qs.exclude(pk=exclude_pagamento_id)
        return qs.aggregate(s=Sum("valor"))["s"] or Decimal("0.00")

    @staticmethod
    def _saldo_disponivel(fatura: Fatura, *, exclude_pagamento_id: int | None = None) -> Decimal:
        comprometido = BillingService._comprometido_pagamentos(
            fatura, exclude_pagamento_id=exclude_pagamento_id
        )
        return max(fatura.total - comprometido, Decimal("0.00"))

    @staticmethod
    def _validar_valor_pagamento(
        fatura: Fatura,
        valor: Decimal,
        *,
        exclude_pagamento_id: int | None = None,
    ) -> None:
        if valor <= 0:
            raise ValueError("O valor do pagamento deve ser positivo.")
        saldo = BillingService._saldo_disponivel(fatura, exclude_pagamento_id=exclude_pagamento_id)
        if valor > saldo:
            raise ValueError("O valor do pagamento não pode ser superior ao saldo da fatura.")

    @staticmethod
    @transaction.atomic
    def cancelar_fatura(fatura_id: int, user, request=None) -> Fatura:
        fatura = Fatura.objects.select_for_update().get(pk=fatura_id)
        if fatura.estado == FaturaEstado.PAGA:
            raise ValueError("Não é possível cancelar uma fatura paga.")
        if fatura.estado == FaturaEstado.CANCELADA:
            raise ValueError("A fatura já está cancelada.")

        fatura.estado = FaturaEstado.CANCELADA
        fatura.save(update_fields=["estado", "updated_at"])

        BillingService._log(
            AuditAction.FACTURA_CANCELADA,
            user,
            request,
            "billing_invoice",
            fatura.pk,
            f"Fatura {fatura.numero} cancelada.",
        )
        BillingCacheService.invalidate_all(patient_id=fatura.paciente_id)
        return fatura

    @staticmethod
    @transaction.atomic
    def registar_pagamento(
        fatura_id: int,
        user,
        *,
        valor: Decimal,
        metodo_pagamento: str,
        referencia: str = "",
        request=None,
    ) -> Pagamento:
        fatura = Fatura.objects.select_for_update().select_related("paciente").get(pk=fatura_id)
        if fatura.estado == FaturaEstado.CANCELADA:
            raise ValueError("Não é possível registar pagamento numa fatura cancelada.")
        if fatura.estado == FaturaEstado.PAGA:
            raise ValueError("A fatura já está totalmente paga.")
        BillingService._validar_valor_pagamento(fatura, valor)

        pagamento = Pagamento.objects.create(
            fatura=fatura,
            metodo_pagamento=metodo_pagamento,
            valor=valor,
            referencia=referencia,
            estado=PagamentoEstado.PENDENTE,
            recebido_por=user,
        )

        BillingService._log(
            AuditAction.PAGAMENTO_REALIZADO,
            user,
            request,
            "billing_payment",
            pagamento.pk,
            f"Pagamento registado para fatura {fatura.numero}.",
            {"fatura_id": fatura.pk, "valor": str(valor)},
        )
        BillingCacheService.invalidate_all(patient_id=fatura.paciente_id)
        return pagamento

    @staticmethod
    @transaction.atomic
    def confirmar_pagamento(pagamento_id: int, user, request=None) -> Pagamento:
        pagamento = (
            Pagamento.objects.select_for_update()
            .select_related("fatura", "fatura__paciente")
            .get(pk=pagamento_id)
        )
        if pagamento.estado != PagamentoEstado.PENDENTE:
            raise ValueError("Apenas pagamentos pendentes podem ser confirmados.")

        fatura = Fatura.objects.select_for_update().get(pk=pagamento.fatura_id)
        if fatura.estado == FaturaEstado.CANCELADA:
            raise ValueError("Não é possível confirmar pagamento numa fatura cancelada.")
        BillingService._validar_valor_pagamento(
            fatura,
            pagamento.valor,
            exclude_pagamento_id=pagamento.pk,
        )

        now = timezone.now()
        pagamento.estado = PagamentoEstado.CONFIRMADO
        pagamento.data_pagamento = now
        pagamento.recebido_por = user
        pagamento.save(update_fields=["estado", "data_pagamento", "recebido_por", "updated_at"])

        BillingService._actualizar_estado_fatura(fatura)
        BillingService.emitir_recibo(pagamento.pk, user, request=request)

        BillingService._log(
            AuditAction.PAGAMENTO_CONFIRMADO,
            user,
            request,
            "billing_payment",
            pagamento.pk,
            f"Pagamento confirmado — fatura {fatura.numero}.",
        )
        event_bus.publish(
            EventNames.BILLING_PAYMENT_CONFIRMED,
            {
                "pagamento_id": pagamento.pk,
                "fatura_id": fatura.pk,
                "paciente_id": fatura.paciente_id,
            },
        )

        from apps.billing.tasks import actualizar_dashboard_financeiro

        actualizar_dashboard_financeiro.delay()

        from apps.finance.services.finance_service import FinanceService

        FinanceService.processar_pagamento_billing(pagamento.pk, user, request=request)

        BillingCacheService.invalidate_all(patient_id=fatura.paciente_id)
        return pagamento

    @staticmethod
    @transaction.atomic
    def emitir_recibo(pagamento_id: int, user, request=None, *, segunda_via: bool = False) -> Recibo:
        pagamento = Pagamento.objects.select_related("fatura").get(pk=pagamento_id)
        if pagamento.estado != PagamentoEstado.CONFIRMADO:
            raise ValueError("Apenas pagamentos confirmados geram recibo.")
        if hasattr(pagamento, "recibo"):
            recibo = pagamento.recibo
            if segunda_via and not recibo.segunda_via:
                recibo.segunda_via = True
                recibo.save(update_fields=["segunda_via", "updated_at"])
            return recibo

        recibo = Recibo.objects.create(
            numero=BillingNumberService.generate_receipt(),
            pagamento=pagamento,
            segunda_via=segunda_via,
        )

        BillingService._log(
            AuditAction.RECIBO_EMITIDO,
            user,
            request,
            "billing_receipt",
            recibo.pk,
            f"Recibo {recibo.numero} emitido.",
            {"pagamento_id": pagamento.pk, "fatura_id": pagamento.fatura_id},
        )
        event_bus.publish(
            EventNames.BILLING_RECEIPT_CREATED,
            {
                "recibo_id": recibo.pk,
                "pagamento_id": pagamento.pk,
                "fatura_id": pagamento.fatura_id,
            },
        )
        BillingCacheService.invalidate_all(patient_id=pagamento.fatura.paciente_id)
        return recibo

    @staticmethod
    def historico_financeiro(patient_id: int) -> dict:
        faturas = (
            Fatura.objects.filter(paciente_id=patient_id)
            .prefetch_related("itens__servico", "pagamentos")
            .order_by("-emitida_em")
        )
        orcamentos = (
            Orcamento.objects.filter(paciente_id=patient_id)
            .prefetch_related("itens__servico")
            .order_by("-created_at")
        )
        recibos = (
            Recibo.objects.filter(pagamento__fatura__paciente_id=patient_id)
            .select_related("pagamento", "pagamento__fatura")
            .order_by("-emitido_em")
        )

        total_faturado = faturas.exclude(estado=FaturaEstado.CANCELADA).aggregate(
            s=Sum("total")
        )["s"] or Decimal("0.00")
        total_pago = Pagamento.objects.filter(
            fatura__paciente_id=patient_id,
            estado=PagamentoEstado.CONFIRMADO,
        ).aggregate(s=Sum("valor"))["s"] or Decimal("0.00")

        return {
            "paciente_id": patient_id,
            "resumo": {
                "total_faturado": str(total_faturado),
                "total_pago": str(total_pago),
                "saldo": str(total_faturado - total_pago),
            },
            "faturas": [
                {
                    "id": f.pk,
                    "numero": f.numero,
                    "estado": f.estado,
                    "total": str(f.total),
                    "emitida_em": f.emitida_em.isoformat() if f.emitida_em else None,
                }
                for f in faturas
            ],
            "orcamentos": [
                {
                    "id": o.pk,
                    "numero": o.numero,
                    "estado": o.estado,
                    "total": str(o.total),
                    "validade": o.validade.isoformat() if o.validade else None,
                }
                for o in orcamentos
            ],
            "recibos": [
                {
                    "id": r.pk,
                    "numero": r.numero,
                    "emitido_em": r.emitido_em.isoformat(),
                    "fatura_numero": r.pagamento.fatura.numero,
                    "valor": str(r.pagamento.valor),
                }
                for r in recibos
            ],
        }

    @staticmethod
    def get_dashboard_summary() -> dict:
        today = timezone.localdate()
        month_start = today.replace(day=1)

        faturas_hoje = Fatura.objects.filter(emitida_em__date=today).exclude(
            estado=FaturaEstado.CANCELADA
        )
        receita_hoje = (
            Pagamento.objects.filter(
                estado=PagamentoEstado.CONFIRMADO,
                data_pagamento__date=today,
            ).aggregate(s=Sum("valor"))["s"]
            or Decimal("0.00")
        )
        receita_mensal = (
            Pagamento.objects.filter(
                estado=PagamentoEstado.CONFIRMADO,
                data_pagamento__date__gte=month_start,
            ).aggregate(s=Sum("valor"))["s"]
            or Decimal("0.00")
        )

        from django.db.models import Count

        servicos_mais_vendidos = list(
            ItemFatura.objects.values("servico__nome")
            .annotate(total=Sum("quantidade"))
            .order_by("-total")[:5]
        )

        return {
            "indicadores": {
                "receita_hoje": float(receita_hoje),
                "receita_mensal": float(receita_mensal),
                "faturas_pendentes": Fatura.objects.filter(estado=FaturaEstado.PENDENTE).count(),
                "faturas_pagas": Fatura.objects.filter(estado=FaturaEstado.PAGA).count(),
                "pagamentos_do_dia": Pagamento.objects.filter(
                    estado=PagamentoEstado.CONFIRMADO,
                    data_pagamento__date=today,
                ).count(),
                "faturas_emitidas_hoje": faturas_hoje.count(),
            },
            "servicos_mais_vendidos": [
                {"servico": s["servico__nome"], "quantidade": s["total"] or 0}
                for s in servicos_mais_vendidos
            ],
        }
