"""Testes do event bus."""

from core.events import DomainEvent, EventNames, event_bus
from core.events.subscribers import subscribers


def test_publish_creates_domain_event():
    event = event_bus.publish(EventNames.USER_CREATED, {"user_id": 1})
    assert isinstance(event, DomainEvent)
    assert event.name == EventNames.USER_CREATED
    assert event.payload["user_id"] == 1


def test_subscribe_handler_is_called():
    received: list[DomainEvent] = []

    def handler(event: DomainEvent) -> None:
        received.append(event)

    subscribers.subscribe("test.event", handler)
    event_bus.publish("test.event", {"ok": True})
    assert len(received) == 1
    assert received[0].payload["ok"] is True
