"""Modelos de analytics."""

from django.db import models


class AnalyticsEvent(models.Model):
    event_name = models.CharField("Evento", max_length=100)
    payload = models.JSONField("Dados", default=dict, blank=True)
    recorded_at = models.DateTimeField("Registado em", auto_now_add=True)

    class Meta:
        verbose_name = "Evento de analytics"
        verbose_name_plural = "Eventos de analytics"
        ordering = ["-recorded_at"]
