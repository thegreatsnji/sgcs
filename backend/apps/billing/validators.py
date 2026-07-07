"""Validadores do módulo de faturação."""

from apps.billing.constants import FaturaEstado
from apps.billing.models import Fatura


def validate_fatura_editavel(fatura: Fatura) -> None:
    if not fatura.is_editavel:
        raise ValueError("Não é possível alterar uma fatura paga ou cancelada.")
    if fatura.estado == FaturaEstado.PAGA:
        raise ValueError("Não é permitido editar uma fatura paga.")


def validate_consulta_sem_fatura(consulta_id: int | None) -> None:
    if consulta_id and Fatura.objects.filter(consulta_id=consulta_id).exclude(
        estado=FaturaEstado.CANCELADA
    ).exists():
        raise ValueError("Esta consulta já possui uma fatura activa.")
