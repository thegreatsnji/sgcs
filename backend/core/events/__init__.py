"""Infraestrutura de eventos do SGCS."""

from core.events.event_bus import event_bus
from core.events.events import DomainEvent, EventNames
from core.events.subscribers import subscribers

__all__ = ["DomainEvent", "EventNames", "event_bus", "subscribers"]
