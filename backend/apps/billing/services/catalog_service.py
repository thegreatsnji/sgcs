"""Serviços de catálogo e histórico de preços."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation

from django.db import transaction

from django.utils import timezone

from apps.audit_logs.models import AuditAction, AuditLog
from apps.audit_logs.services import AuditService, get_client_info
from apps.authentication.models import UserRole
from apps.billing.constants import DEFAULT_SERVICE_CURRENCY, PRICE_REVIEW_MARKER
from apps.billing.models import Servico, ServicoPrecoHistorico


def parse_preco_fcfa(raw: str | None) -> tuple[Decimal | None, bool]:
    """
    Devolve (preço, pendente_revisão).
    Valores vazios ou REVISAR_COM_CLINICA => pendente, não importável em --apply.
    """
    if raw is None:
        return None, True
    value = str(raw).strip()
    if not value or value.upper() == PRICE_REVIEW_MARKER:
        return None, True
    try:
        amount = Decimal(value.replace(",", ".").replace(" ", ""))
    except InvalidOperation as exc:
        raise ValueError(f"Preço inválido: {raw}") from exc
    if amount < 0:
        raise ValueError("O preço não pode ser negativo.")
    if amount != amount.to_integral_value():
        amount = amount.quantize(Decimal("1"))
    return amount, False


ORIGEM_IMPORTACAO_VALIDADA = "IMPORTACAO_VALIDADA"

MSG_PRECO_NAO_CONFIRMADO = (
    "O preço deste serviço ainda não foi confirmado pela clínica. Contacte o Administrador."
)


def servico_pode_faturar(servico: Servico, user=None) -> bool:
    if not servico.activo:
        return False
    if servico.preco_confirmado:
        return True
    if servico.permite_faturacao_sem_preco_confirmado:
        return True
    if user and user_pode_alterar_preco(user):
        return True
    return False


def assert_servico_faturavel(servico: Servico, user=None) -> None:
    if servico_pode_faturar(servico, user):
        return
    raise ValueError(MSG_PRECO_NAO_CONFIRMADO)


def confirmar_preco_servico(
    servico: Servico,
    preco: Decimal,
    *,
    user,
    request=None,
    motivo: str = "",
    origem: str = ORIGEM_IMPORTACAO_VALIDADA,
    confirmado_por_nome: str = "",
) -> Servico:
    preco_anterior = servico.preco
    if preco != preco_anterior:
        registar_alteracao_preco(
            servico,
            preco_anterior,
            preco,
            user=user,
            request=request,
            motivo=motivo or confirmado_por_nome,
            origem=origem,
        )
    servico.preco = preco
    servico.preco_confirmado = True
    servico.preco_confirmado_em = timezone.now()
    if user and user.is_authenticated:
        servico.preco_confirmado_por = user
    servico.save(
        update_fields=[
            "preco",
            "preco_confirmado",
            "preco_confirmado_em",
            "preco_confirmado_por",
            "updated_at",
        ]
    )
    return servico


def user_pode_alterar_preco(user) -> bool:
    if not user or not user.is_authenticated:
        return False
    return user.is_superuser or user.role == UserRole.ADMINISTRADOR


def registar_alteracao_preco(
    servico: Servico,
    preco_anterior: Decimal,
    preco_novo: Decimal,
    *,
    user,
    request=None,
    motivo: str = "",
    origem: str = "manual",
) -> ServicoPrecoHistorico:
    historico = ServicoPrecoHistorico.objects.create(
        servico=servico,
        preco_anterior=preco_anterior,
        preco_novo=preco_novo,
        motivo=motivo,
        origem=origem,
        alterado_por=user,
        ip_address=get_client_info(request)[0] if request else None,
    )
    AuditService.log(
        action=AuditAction.SERVICO_PRECO_ALTERADO,
        user=user,
        request=request,
        description=(
            f"Preço do serviço {servico.codigo} alterado de {preco_anterior} para {preco_novo} FCFA."
        ),
        resource_type="Servico",
        resource_id=str(servico.pk),
        metadata={
            "codigo": servico.codigo,
            "preco_anterior": str(preco_anterior),
            "preco_novo": str(preco_novo),
            "origem": origem,
            "motivo": motivo,
        },
    )
    return historico


@transaction.atomic
def actualizar_servico_com_auditoria(servico: Servico, data: dict, *, user, request=None) -> Servico:
    preco_novo = data.get("preco")
    if preco_novo is not None and preco_novo != servico.preco:
        if not user_pode_alterar_preco(user):
            raise ValueError("Apenas o administrador pode alterar o preço oficial do serviço.")
        parse_preco_fcfa(str(preco_novo))  # valida
        registar_alteracao_preco(
            servico,
            servico.preco,
            Decimal(str(preco_novo)),
            user=user,
            request=request,
            motivo=data.get("motivo_alteracao_preco", ""),
            origem="manual",
        )

    for field, value in data.items():
        if field in ("motivo_alteracao_preco",):
            continue
        if hasattr(servico, field):
            setattr(servico, field, value)
    servico.actualizado_por = user
    if not servico.moeda:
        servico.moeda = DEFAULT_SERVICE_CURRENCY
    servico.save()
    return servico
