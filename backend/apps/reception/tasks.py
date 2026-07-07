"""Tarefas Celery do módulo de receção (preparadas para Sprint futura)."""

from config.celery import app


@app.task(name="reception.send_wait_reminder", bind=True)
def send_wait_reminder(self, queue_entry_id: int) -> dict:
    """Stub: lembrete de espera prolongada (não implementado)."""
    return {"queue_entry_id": queue_entry_id, "ready": False}
