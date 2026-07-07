"""Tarefas Celery do SGCS."""

from config.celery import app


@app.task(name="sgcs.ping")
def ping() -> str:
    return "pong"
