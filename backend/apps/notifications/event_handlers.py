"""Handlers de eventos do Event Bus para notificações."""

from __future__ import annotations

import logging

from apps.authentication.models import User, UserRole
from apps.notifications.constants import NotificacaoCanal, NotificacaoTipo
from apps.notifications.services.notification_service import NotificationService
from core.events.events import DomainEvent, EventNames
from core.events.subscribers import subscribers

logger = logging.getLogger(__name__)

EVENTO_TITULOS = {
    EventNames.PATIENT_CREATED: ("Novo paciente", NotificacaoTipo.INFORMATIVA),
    EventNames.PATIENT_UPDATED: ("Paciente actualizado", NotificacaoTipo.INFORMATIVA),
    EventNames.PATIENT_DEACTIVATED: ("Paciente desactivado", NotificacaoTipo.AVISO),
    EventNames.LABORATORY_RESULT_PUBLISHED: ("Resultado laboratorial publicado", NotificacaoTipo.SUCESSO),
    EventNames.BILLING_INVOICE_CREATED: ("Factura criada", NotificacaoTipo.INFORMATIVA),
    EventNames.BILLING_PAYMENT_CONFIRMED: ("Pagamento confirmado", NotificacaoTipo.SUCESSO),
    EventNames.FINANCE_EXPENSE_CREATED: ("Despesa registada", NotificacaoTipo.INFORMATIVA),
    EventNames.DOCTOR_FOLLOWUP_CREATED: ("Seguimento agendado", NotificacaoTipo.LEMBRETE),
    EventNames.REPORT_GENERATED: ("Relatório gerado", NotificacaoTipo.INFORMATIVA),
    EventNames.BACKUP_CREATED: ("Backup concluído", NotificacaoTipo.SUCESSO),
    EventNames.USER_LOGIN: ("Sessão iniciada", NotificacaoTipo.INFORMATIVA),
    "appointment.created": ("Consulta agendada", NotificacaoTipo.INFORMATIVA),
    "appointment.confirmed": ("Consulta confirmada", NotificacaoTipo.SUCESSO),
    "appointment.cancelled": ("Consulta cancelada", NotificacaoTipo.AVISO),
}


def _destinatarios_por_evento(event: DomainEvent) -> list[User]:
    if event.name in {
        EventNames.LABORATORY_RESULT_PUBLISHED,
        EventNames.DOCTOR_PRESCRIPTION_CREATED,
        EventNames.DOCTOR_FOLLOWUP_CREATED,
    }:
        return list(User.objects.filter(role=UserRole.MEDICO, is_active=True))
    if event.name in {EventNames.BILLING_INVOICE_CREATED, EventNames.BILLING_PAYMENT_CONFIRMED}:
        return list(User.objects.filter(role=UserRole.FINANCEIRO, is_active=True))
    if event.name in {EventNames.BACKUP_CREATED, EventNames.BACKUP_RESTORED, EventNames.SYSTEM_UPDATED}:
        return list(User.objects.filter(role=UserRole.ADMINISTRADOR, is_active=True))
    if event.name in {EventNames.PATIENT_CREATED, "appointment.created"}:
        return list(User.objects.filter(role__in=[UserRole.RECECIONISTA, UserRole.MEDICO], is_active=True))
    return []


def handle_domain_event(event: DomainEvent) -> None:
    titulo_info = EVENTO_TITULOS.get(event.name)
    if not titulo_info:
        return
    titulo, tipo = titulo_info
    mensagem = f"Evento {event.name} processado. Detalhes: {event.payload}"
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
            metadados=event.payload,
        )


def register_notification_handlers() -> None:
    eventos = [
        EventNames.PATIENT_CREATED,
        EventNames.PATIENT_UPDATED,
        EventNames.PATIENT_DEACTIVATED,
        EventNames.LABORATORY_RESULT_PUBLISHED,
        EventNames.LABORATORY_RESULT_CREATED,
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
