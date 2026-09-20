"""Regras operacionais de regularização financeira no laboratório."""

from apps.appointments.constants import PedidoLaboratorioEstadoFaturacao
from apps.laboratory.models import PedidoLaboratorial

MSG_AGUARDA_REGULARIZACAO = "Este exame aguarda regularização na Receção."

ESTADO_FATURACAO_LABELS = {
    PedidoLaboratorioEstadoFaturacao.AGUARDA_REGULARIZACAO: "Aguarda regularização",
    PedidoLaboratorioEstadoFaturacao.REGULARIZADO: "Regularizado",
    PedidoLaboratorioEstadoFaturacao.NAO_APLICAVEL: "Não aplicável",
}


def get_estado_faturacao(pedido: PedidoLaboratorial) -> str:
    if not pedido.pedido_consulta_id:
        return PedidoLaboratorioEstadoFaturacao.NAO_APLICAVEL
    return pedido.pedido_consulta.estado_faturacao


def get_estado_faturacao_label(pedido: PedidoLaboratorial) -> str:
    code = get_estado_faturacao(pedido)
    return ESTADO_FATURACAO_LABELS.get(code, code)


def aguarda_regularizacao(pedido: PedidoLaboratorial) -> bool:
    return get_estado_faturacao(pedido) == PedidoLaboratorioEstadoFaturacao.AGUARDA_REGULARIZACAO


def pode_iniciar_processamento(pedido: PedidoLaboratorial) -> bool:
    return not aguarda_regularizacao(pedido)


def ensure_pode_processar(pedido: PedidoLaboratorial) -> None:
    if aguarda_regularizacao(pedido):
        raise ValueError(MSG_AGUARDA_REGULARIZACAO)
