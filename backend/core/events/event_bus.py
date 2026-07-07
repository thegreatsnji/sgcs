"""Event bus do SGCS — publicação e subscrição de eventos."""

from __future__ import annotations

from typing import Any

from core.events.dispatcher import dispatcher
from core.events.events import DomainEvent
from core.events.subscribers import register_default_subscribers, subscribers

register_default_subscribers()


class EventBus:
    def publish(self, name: str, payload: dict[str, Any] | None = None) -> DomainEvent:
        event = DomainEvent(name=name, payload=payload or {})
        dispatcher.dispatch(event)
        return event

    def subscribe(self, event_name: str, handler) -> None:
        subscribers.subscribe(event_name, handler)


event_bus = EventBus()
