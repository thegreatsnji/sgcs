"""Handlers de eventos do Event Bus para notificações."""

from __future__ import annotations

import logging

from apps.authentication.models import User, UserRole
from apps.notifications.constants import NotificacaoCanal, NotificacaoTipo
from apps.notifications.services.notification_service import NotificationService
from core.events.events import DomainEvent, EventNames
from core.events.subscribers import subscribers

logger = logging.getLogger(__name__)

# Eventos clínicos/operacionais com título legível.
# laboratory.result.validated → tratado em result_notification (médico solicitante).
# laboratory.result.published (Entregue) → sem broadcast; validação já alertou o médico.
EVENTO_TITULOS = {
    EventNames.PATIENT_CREATED: ("Novo paciente", NotificacaoTipo.INFORMATIVA),
    EventNames.PATIENT_DEACTIVATED: ("Paciente desactivado", NotificacaoTipo.AVISO),
    EventNames.BILLING_PAYMENT_CONFIRMED: ("Pagamento confirmado", NotificacaoTipo.SUCESSO),
    EventNames.DOCTOR_FOLLOWUP_CREATED: ("Seguimento agendado", NotificacaoTipo.LEMBRETE),
    EventNames.BACKUP_CREATED: ("Backup concluído", NotificacaoTipo.SUCESSO),
    "appointment.created": ("Consulta agendada", NotificacaoTipo.INFORMATIVA),
    "appointment.confirmed": ("Consulta confirmada", NotificacaoTipo.SUCESSO),
    "appointment.cancelled": ("Consulta cancelada", NotificacaoTipo.AVISO),
}


def _mensagem_legivel(event: DomainEvent, titulo: str) -> str:
    payload = event.payload or {}
    if event.name == EventNames.PATIENT_CREATED:
        pid = payload.get("patient_id")
        return f"Foi registado um novo paciente{f' (#{pid})' if pid else ''}."
    if event.name.startswith("appointment."):
        aid = payload.get("appointment_id") or payload.get("consulta_id")
        return f"{titulo}{f' — consulta #{aid}' if aid else ''}."
    if event.name == EventNames.BILLING_PAYMENT_CONFIRMED:
        fatura = payload.get("fatura_id") or payload.get("invoice_id")
        return f"Pagamento confirmado{f' (factura #{fatura})' if fatura else ''}."
    if event.name == EventNames.DOCTOR_FOLLOWUP_CREATED:
        return "Foi agendado um seguimento clínico."
    if event.name == EventNames.BACKUP_CREATED:
        return "Cópia de segurança concluída com sucesso."
    if event.name == EventNames.PATIENT_DEACTIVATED:
        pid = payload.get("patient_id")
        return f"Paciente desactivado{f' (#{pid})' if pid else ''}."
    return titulo


def _destinatarios_por_evento(event: DomainEvent) -> list[User]:
    if event.name == EventNames.DOCTOR_FOLLOWUP_CREATED:
        return list(User.objects.filter(role=UserRole.MEDICO, is_active=True))
    if event.name == EventNames.BILLING_PAYMENT_CONFIRMED:
        return list(User.objects.filter(role=UserRole.FINANCEIRO, is_active=True))
    if event.name in {EventNames.BACKUP_CREATED, EventNames.BACKUP_RESTORED, EventNames.SYSTEM_UPDATED}:
        return list(User.objects.filter(role=UserRole.ADMINISTRADOR, is_active=True))
    if event.name in {EventNames.PATIENT_CREATED, "appointment.created"}:
        # Receção operacional; médicos já vêem filas — evita spam a todos os médicos.
        return list(User.objects.filter(role=UserRole.RECECIONISTA, is_active=True))
    if event.name in {"appointment.confirmed", "appointment.cancelled"}:
        return list(User.objects.filter(role=UserRole.RECECIONISTA, is_active=True))
    return []


def handle_domain_event(event: DomainEvent) -> None:
    titulo_info = EVENTO_TITULOS.get(event.name)
    if not titulo_info:
        return
    titulo, tipo = titulo_info
    mensagem = _mensagem_legivel(event, titulo)
    destinatarios = _destinatarios_por_evento(event)

    if event.name in {EventNames.BACKUP_CREATED, EventNames.BACKUP_RESTORED}:
        NotificationService.notificar_administradores(titulo, mensagem, event.name, tipo=tipo)
        return

    for user in destinatarios:
        NotificationService.criar(
            titulo=titulo,
            mensagem=mensagem,
            utilizador=user,
            tipo=tipo,
            canal=NotificacaoCanal.INTERNO,
            evento_origem=event.name,
            metadados=event.payload if isinstance(event.payload, dict) else {},
        )


def register_notification_handlers() -> None:
    eventos = [
        EventNames.PATIENT_CREATED,
        EventNames.PATIENT_UPDATED,
        EventNames.PATIENT_DEACTIVATED,
        EventNames.LABORATORY_RESULT_PUBLISHED,
        EventNames.LABORATORY_RESULT_CREATED,
        EventNames.LABORATORY_RESULT_VALIDATED,
        EventNames.BILLING_QUOTE_CREATED,
        EventNames.BILLING_INVOICE_CREATED,
        EventNames.BILLING_PAYMENT_CONFIRMED,
        EventNames.BILLING_RECEIPT_CREATED,
        EventNames.FINANCE_CASH_OPENED,
        EventNames.FINANCE_CASH_CLOSED,
        EventNames.FINANCE_EXPENSE_CREATED,
        EventNames.FINANCE_PAYMENT_RECEIVED,
        EventNames.FINANCE_REPORT_GENERATED,
        EventNames.REPORT_GENERATED,
        EventNames.DASHBOARD_UPDATED,
        EventNames.STATISTICS_UPDATED,
        EventNames.SETTINGS_UPDATED,
        EventNames.BACKUP_CREATED,
        EventNames.BACKUP_RESTORED,
        EventNames.SYSTEM_UPDATED,
        EventNames.DOCTOR_PRESCRIPTION_CREATED,
        EventNames.DOCTOR_DISCHARGE_CREATED,
        EventNames.DOCTOR_FOLLOWUP_CREATED,
        EventNames.USER_CREATED,
        EventNames.USER_UPDATED,
        EventNames.USER_LOGIN,
        EventNames.USER_LOGOUT,
        "appointment.created",
        "appointment.confirmed",
        "appointment.cancelled",
    ]
    for nome in eventos:
        subscribers.subscribe(nome, handle_domain_event)
    logger.info("Handlers de notificação registados para %s eventos.", len(eventos))
