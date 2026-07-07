"""Tarefas Celery do módulo de consultas."""

from celery import shared_task


@shared_task(name="appointments.send_appointment_reminder")
def send_appointment_reminder(appointment_id: int) -> dict:
    """Stub preparado para lembretes de consulta (Sprint futura)."""
    return {"appointment_id": appointment_id, "status": "scheduled", "sent": False}
