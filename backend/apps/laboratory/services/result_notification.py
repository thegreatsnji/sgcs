"""Notificações clínicas geradas pelo laboratório."""

from __future__ import annotations

import logging

from apps.notifications.constants import NotificacaoCanal, NotificacaoTipo
from apps.notifications.services.notification_service import NotificationService
from core.events.events import EventNames

logger = logging.getLogger(__name__)


def _exame_label(pedido) -> str:
    nomes = list(pedido.exames.values_list("nome_exame", flat=True))
    if not nomes and pedido.pedido_consulta_id:
        tipo = getattr(pedido.pedido_consulta, "tipo_exame", "") or ""
        if tipo:
            nomes = [tipo]
    if not nomes:
        return "exame laboratorial"
    if len(nomes) == 1:
        return nomes[0]
    if len(nomes) <= 3:
        return ", ".join(nomes)
    return f"{', '.join(nomes[:2])} (+{len(nomes) - 2})"


def notify_ordering_doctor_result_validated(resultado_id: int) -> dict:
    """Alerta o médico que pediu o exame — resultado validado e disponível."""
    from apps.laboratory.models import ResultadoLaboratorial

    try:
        resultado = ResultadoLaboratorial.objects.select_related(
            "pedido_laboratorial__paciente",
            "pedido_laboratorial__medico",
            "pedido_laboratorial__consulta__doctor",
            "pedido_laboratorial__pedido_consulta",
        ).get(pk=resultado_id)
    except ResultadoLaboratorial.DoesNotExist:
        return {"status": "not_found", "resultado_id": resultado_id}

    pedido = resultado.pedido_laboratorial
    medico = pedido.medico or getattr(pedido.consulta, "doctor", None)
    if medico is None or not medico.is_active:
        logger.info(
            "Sem médico destinatário para resultado %s (pedido %s).",
            resultado_id,
            pedido.numero_pedido,
        )
        return {"status": "no_doctor", "resultado_id": resultado_id}

    paciente = pedido.paciente
    exame = _exame_label(pedido)
    titulo = f"Resultado validado — {exame}"
    mensagem = (
        f"{paciente.full_name} ({paciente.patient_number}): "
        f"resultado de {exame} disponível (pedido {pedido.numero_pedido})."
    )
    metadados = {
        "resultado_id": resultado.pk,
        "pedido_id": pedido.pk,
        "patient_id": paciente.pk,
        "consulta_id": pedido.consulta_id,
        "numero_pedido": pedido.numero_pedido,
        "url": f"/laboratory/results/{resultado.pk}",
        "patient_url": f"/patients/{paciente.pk}",
    }

    notif = NotificationService.criar(
        titulo=titulo,
        mensagem=mensagem,
        utilizador=medico,
        tipo=NotificacaoTipo.SUCESSO,
        canal=NotificacaoCanal.INTERNO,
        evento_origem=EventNames.LABORATORY_RESULT_VALIDATED,
        metadados=metadados,
    )
    return {
        "status": "ok" if notif else "skipped_preference",
        "resultado_id": resultado_id,
        "medico_id": medico.pk,
        "notificacao_id": notif.pk if notif else None,
    }
