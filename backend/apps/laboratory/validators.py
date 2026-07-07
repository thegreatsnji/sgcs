"""Validadores do módulo de laboratório."""

from apps.laboratory.constants import FINAL_STATUSES, PedidoLaboratorialEstado


def validate_pedido_editavel(estado: str) -> None:
    if estado in FINAL_STATUSES:
        raise ValueError("Não é possível alterar um pedido concluído ou cancelado.")


def validate_transicao(estado_atual: str, estados_permitidos: set[str], acao: str) -> None:
    if estado_atual not in estados_permitidos:
        raise ValueError(f"Não é possível {acao} neste estado ({estado_atual}).")
