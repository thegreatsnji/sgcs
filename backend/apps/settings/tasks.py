"""Tarefas Celery do módulo de configurações (stubs)."""

from config.celery import app


@app.task(name="settings.backup_database")
def backup_database(backup_id: int) -> dict:
    return {"status": "stub", "backup_id": backup_id}


@app.task(name="settings.restore_database")
def restore_database(backup_id: int) -> dict:
    return {"status": "stub", "backup_id": backup_id}


@app.task(name="settings.send_test_email")
def send_test_email() -> dict:
    return {"status": "stub", "action": "send_test_email"}


@app.task(name="settings.cleanup_storage")
def cleanup_storage() -> dict:
    return {"status": "stub", "action": "cleanup_storage"}


@app.task(name="settings.cleanup_logs")
def cleanup_logs() -> dict:
    return {"status": "stub", "action": "cleanup_logs"}
