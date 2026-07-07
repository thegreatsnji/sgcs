"""Tarefa Celery base com retry e dead-letter básico."""

import logging

from celery import Task

logger = logging.getLogger(__name__)


class SGCSBaseTask(Task):
    autoretry_for = (Exception,)
    retry_kwargs = {"max_retries": 3, "countdown": 30}
    retry_backoff = True
    retry_jitter = True

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logger.error(
            "Tarefa falhou (dead-letter): task=%s id=%s erro=%s",
            self.name,
            task_id,
            exc,
        )
        super().on_failure(exc, task_id, args, kwargs, einfo)
