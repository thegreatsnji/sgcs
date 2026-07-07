"""Configuração Celery do SGCS."""

import os

from celery import Celery

from core.tasks.base import SGCSBaseTask

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

app = Celery("sgcs")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.Task = SGCSBaseTask
app.autodiscover_tasks()
app.autodiscover_tasks(["config"])
