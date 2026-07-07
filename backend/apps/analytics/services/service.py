"""Serviços de analytics."""


class AnalyticsService:
    @staticmethod
    def record_event(event_name: str, payload: dict | None = None):
        from apps.analytics.models import AnalyticsEvent

        return AnalyticsEvent.objects.create(event_name=event_name, payload=payload or {})
