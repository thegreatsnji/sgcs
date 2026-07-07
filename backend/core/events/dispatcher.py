"""Dispatcher de eventos do SGCS."""

from __future__ import annotations

import logging

from core.config.feature_flags import is_feature_enabled
from core.events.events import DomainEvent
from core.events.subscribers import subscribers

logger = logging.getLogger(__name__)


class EventDispatcher:
    def dispatch(self, event: DomainEvent) -> None:
        if not is_feature_enabled("event_bus_enabled"):
            return

        handlers = subscribers.get_handlers(event.name)
        for handler in handlers:
            try:
                handler(event)
            except Exception:
                logger.exception("Erro ao processar evento %s", event.name)

    def dispatch_many(self, events: list[DomainEvent]) -> None:
        for event in events:
            self.dispatch(event)


dispatcher = EventDispatcher()
