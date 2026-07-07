"""Subscritores de eventos do SGCS."""

from __future__ import annotations

import logging
from collections.abc import Callable

from core.events.events import DomainEvent

logger = logging.getLogger(__name__)

EventHandler = Callable[[DomainEvent], None]


class EventSubscribers:
    def __init__(self) -> None:
        self._handlers: dict[str, list[EventHandler]] = {}

    def subscribe(self, event_name: str, handler: EventHandler) -> None:
        self._handlers.setdefault(event_name, []).append(handler)

    def get_handlers(self, event_name: str) -> list[EventHandler]:
        return list(self._handlers.get(event_name, []))

    def all_event_names(self) -> list[str]:
        return sorted(self._handlers.keys())


subscribers = EventSubscribers()


def register_default_subscribers() -> None:
    def log_event(event: DomainEvent) -> None:
        logger.info("Evento publicado: %s | payload=%s", event.name, event.payload)

    for event_name in (
        "user.created",
        "user.updated",
        "user.deleted",
        "user.login",
        "user.logout",
        "file.uploaded",
        "settings.updated",
        "analytics.recorded",
        "patient.created",
        "patient.updated",
        "patient.deactivated",
        "laboratory.result.created",
        "laboratory.result.validated",
        "laboratory.result.published",
        "billing.quote.created",
        "billing.invoice.created",
        "billing.payment.confirmed",
        "billing.receipt.created",
        "finance.cash.opened",
        "finance.cash.closed",
        "finance.expense.created",
        "finance.payment.received",
        "finance.report.generated",
        "report.generated",
        "dashboard.updated",
        "statistics.updated",
        "settings.updated",
        "backup.created",
        "backup.restored",
        "system.updated",
        "doctor.prescription.created",
        "doctor.discharge.created",
        "doctor.followup.created",
    ):
        subscribers.subscribe(event_name, log_event)
