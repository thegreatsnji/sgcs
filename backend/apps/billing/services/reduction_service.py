"""Cálculo e validação de reduções de valor na faturação."""

from __future__ import annotations

from decimal import Decimal

from django.db import transaction

from django.utils import timezone

from apps.audit_logs.models import AuditAction
from apps.audit_logs.services import AuditService
from apps.authentication.models import UserRole
from apps.billing.constants import (
    EstadoAutorizacaoReducao,
    MotivoReducao,
    OrigemPrecoItem,
)
from apps.billing.models import ReducaoValorAutorizacao, Servico
from apps.settings.models import ConfiguracaoFaturacao
from apps.settings.services.settings_service import SettingsService


class ReductionError(ValueError):
    pass


def _billing_settings() -> ConfiguracaoFaturacao:
    return SettingsService._get_singleton(ConfiguracaoFaturacao)


def _percentual(preco_oficial: Decimal, preco_cobrado: Decimal) -> Decimal:
    if preco_oficial <= 0:
        return Decimal("0.00")
    diff = preco_oficial - preco_cobrado
    return (diff / preco_oficial * Decimal("100")).quantize(Decimal("0.01"))


def resolve_item_pricing(
    servico: Servico,
    user,
    *,
    quantidade: int,
    preco_cobrado_raw,
    motivo_reducao: str | None = None,
    observacao_reducao: str | None = None,
    autorizacao_reducao_id: int | None = None,
    request=None,
) -> dict:
    """Devolve campos para ItemFatura; valida limites e autorização."""
    config = _billing_settings()
    preco_oficial = servico.preco
    quantidade = max(1, int(quantidade))

    if preco_cobrado_raw is None:
        preco_cobrado = preco_oficial
    else:
        preco_cobrado = Decimal(str(preco_cobrado_raw)).quantize(Decimal("0.01"))

    if preco_cobrado < 0:
        raise ReductionError("O valor cobrado não pode ser negativo.")
    if preco_cobrado > preco_oficial:
        AuditService.log(
            action=AuditAction.TENTATIVA_ALTERAR_PRECO_OFICIAL,
            user=user,
            request=request,
            description="Tentativa de cobrar acima do preço oficial do catálogo.",
            resource_type="billing_service",
            resource_id=str(servico.pk),
            metadata={
                "preco_oficial": str(preco_oficial),
                "preco_tentado": str(preco_cobrado),
            },
        )
        raise ReductionError("O valor cobrado não pode ser superior ao preço oficial do catálogo.")

    subtotal_oficial = (preco_oficial * quantidade).quantize(Decimal("0.01"))
    subtotal_cobrado = (preco_cobrado * quantidade).quantize(Decimal("0.01"))
    valor_reducao = (subtotal_oficial - subtotal_cobrado).quantize(Decimal("0.01"))
    percentual = _percentual(preco_oficial, preco_cobrado)

    if preco_cobrado == preco_oficial and valor_reducao == 0:
        return {
            "preco": preco_cobrado,
            "preco_oficial": preco_oficial,
            "subtotal": subtotal_cobrado,
            "subtotal_oficial": subtotal_oficial,
            "valor_reducao": Decimal("0.00"),
            "percentual_reducao": Decimal("0.00"),
            "motivo_reducao": "",
            "observacao_reducao": "",
            "origem_preco": OrigemPrecoItem.CATALOGO,
            "estado_autorizacao_reducao": EstadoAutorizacaoReducao.NAO_APLICAVEL,
            "reduzido_por": None,
            "autorizado_por": None,
            "data_reducao": None,
            "autorizacao_reducao": None,
        }

    if not config.permitir_reducao_rececao:
        raise ReductionError("A clínica não permite redução de valores na receção.")

    if preco_cobrado == 0 and not config.permitir_valor_zero:
        raise ReductionError("Valor zero não permitido sem configuração da clínica.")

    if config.exigir_motivo_reducao and not motivo_reducao:
        raise ReductionError("Indique o motivo da redução do valor.")

    if motivo_reducao == MotivoReducao.OUTRO and not (observacao_reducao or "").strip():
        raise ReductionError("Para o motivo «Outro», a observação é obrigatória.")

    limite = config.limite_reducao_rececao_percentual
    acima_limite = (
        limite is not None
        and percentual > limite
        and config.exigir_autorizacao_acima_limite
    )

    if (
        config.exigir_observacao_acima_percentual is not None
        and percentual > config.exigir_observacao_acima_percentual
        and not (observacao_reducao or "").strip()
    ):
        raise ReductionError("Observação obrigatória para reduções acima do limite configurado.")

    autorizacao = None
    estado = EstadoAutorizacaoReducao.APROVADA_AUTOMATICAMENTE
    autorizado_por = None
    origem = OrigemPrecoItem.REDUCAO_RECECAO

    if autorizacao_reducao_id:
        autorizacao = ReducaoValorAutorizacao.objects.select_related("decidido_por").get(
            pk=autorizacao_reducao_id
        )
        if autorizacao.estado != EstadoAutorizacaoReducao.APROVADA:
            raise ReductionError("A autorização de redução não está aprovada.")
        if autorizacao.servico_id != servico.pk:
            raise ReductionError("A autorização não corresponde ao serviço.")
        if autorizacao.preco_proposto != preco_cobrado:
            raise ReductionError("O valor cobrado não coincide com a autorização aprovada.")
        estado = EstadoAutorizacaoReducao.APROVADA
        autorizado_por = autorizacao.decidido_por
        origem = OrigemPrecoItem.REDUCAO_AUTORIZADA
    elif acima_limite:
        raise ReductionError("Esta redução necessita de autorização da Direção.")

    now = timezone.now()
    return {
        "preco": preco_cobrado,
        "preco_oficial": preco_oficial,
        "subtotal": subtotal_cobrado,
        "subtotal_oficial": subtotal_oficial,
        "valor_reducao": valor_reducao,
        "percentual_reducao": percentual,
        "motivo_reducao": motivo_reducao or "",
        "observacao_reducao": observacao_reducao or "",
        "origem_preco": origem,
        "estado_autorizacao_reducao": estado,
        "reduzido_por": user,
        "autorizado_por": autorizado_por,
        "data_reducao": now,
        "autorizacao_reducao": autorizacao,
    }


def solicitar_autorizacao_reducao(
    user,
    *,
    servico_id: int,
    paciente_id: int | None,
    quantidade: int,
    preco_proposto: Decimal,
    motivo_reducao: str,
    observacao: str = "",
    request=None,
) -> ReducaoValorAutorizacao:
    servico = Servico.objects.get(pk=servico_id, activo=True)
    preco_oficial = servico.preco
    preco_proposto = Decimal(str(preco_proposto)).quantize(Decimal("0.01"))
    if preco_proposto > preco_oficial:
        raise ReductionError("O preço proposto não pode exceder o preço oficial.")
    diff = (preco_oficial - preco_proposto).quantize(Decimal("0.01"))
    pct = _percentual(preco_oficial, preco_proposto)
    if motivo_reducao == MotivoReducao.OUTRO and not observacao.strip():
        raise ReductionError("Para o motivo «Outro», a observação é obrigatória.")

    auth = ReducaoValorAutorizacao.objects.create(
        servico=servico,
        paciente_id=paciente_id,
        solicitado_por=user,
        motivo_reducao=motivo_reducao,
        observacao_solicitacao=observacao,
        preco_oficial=preco_oficial,
        preco_proposto=preco_proposto,
        quantidade=max(1, quantidade),
        diferenca_unitaria=diff,
        percentual_reducao=pct,
        estado=EstadoAutorizacaoReducao.PENDENTE,
    )
    AuditService.log(
        action=AuditAction.REDUCAO_VALOR_SOLICITADA,
        user=user,
        request=request,
        description=f"Redução solicitada para {servico.codigo}.",
        resource_type="billing_reduction_auth",
        resource_id=str(auth.pk),
        metadata={
            "preco_oficial": str(preco_oficial),
            "preco_proposto": str(preco_proposto),
            "percentual": str(pct),
            "motivo": motivo_reducao,
        },
    )
    return auth


def decidir_autorizacao_reducao(
    auth_id: int,
    user,
    *,
    aprovar: bool,
    observacao: str = "",
    request=None,
) -> ReducaoValorAutorizacao:
    if user.role not in (UserRole.ADMINISTRADOR, UserRole.DIRECTOR):
        raise ReductionError("Apenas Direção ou Administrador podem decidir autorizações.")

    with transaction.atomic():
        auth = ReducaoValorAutorizacao.objects.select_for_update().get(pk=auth_id)
        if auth.estado != EstadoAutorizacaoReducao.PENDENTE:
            raise ReductionError("Esta autorização já foi decidida.")
        if auth.solicitado_por_id == user.pk:
            raise ReductionError("Não pode decidir uma autorização solicitada por si.")

        now = timezone.now()
        auth.estado = (
            EstadoAutorizacaoReducao.APROVADA if aprovar else EstadoAutorizacaoReducao.REJEITADA
        )
        auth.decidido_por = user
        auth.decidido_em = now
        auth.observacao_decisao = observacao
        auth.save(
            update_fields=[
                "estado",
                "decidido_por",
                "decidido_em",
                "observacao_decisao",
                "updated_at",
            ]
        )
    action = (
        AuditAction.REDUCAO_VALOR_APROVADA if aprovar else AuditAction.REDUCAO_VALOR_REJEITADA
    )
    AuditService.log(
        action=action,
        user=user,
        request=request,
        description=f"Autorização de redução {auth.pk} {'aprovada' if aprovar else 'rejeitada'}.",
        resource_type="billing_reduction_auth",
        resource_id=str(auth.pk),
        metadata={"servico_id": auth.servico_id, "preco_proposto": str(auth.preco_proposto)},
    )
    return auth