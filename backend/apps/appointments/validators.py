"""Validadores do módulo de consultas."""

from datetime import timedelta

from django.utils import timezone

from apps.appointments.constants import ACTIVE_APPOINTMENT_STATUSES, DEFAULT_DURATION_MINUTES
from apps.appointments.models import Appointment


def validate_doctor_availability(
    *,
    doctor_id: int,
    scheduled_at,
    duration_minutes: int = DEFAULT_DURATION_MINUTES,
    exclude_appointment_id: int | None = None,
) -> None:
    """Garante que o médico não tem consultas sobrepostas."""
    if not doctor_id:
        return

    start = scheduled_at
    end = start + timedelta(minutes=duration_minutes)

    overlapping = Appointment.objects.filter(
        doctor_id=doctor_id,
        status__in=ACTIVE_APPOINTMENT_STATUSES,
        scheduled_at__lt=end,
    )
    if exclude_appointment_id:
        overlapping = overlapping.exclude(pk=exclude_appointment_id)

    for appointment in overlapping:
        other_start = appointment.scheduled_at
        other_end = other_start + timedelta(minutes=appointment.duration_minutes or DEFAULT_DURATION_MINUTES)
        if other_end > start and other_start < end:
            raise ValueError(
                f"O médico já tem consulta agendada às {other_start.strftime('%H:%M')}."
            )


def validate_scheduled_in_future(scheduled_at) -> None:
    if scheduled_at < timezone.now() - timedelta(minutes=5):
        raise ValueError("A data da consulta não pode ser no passado.")
