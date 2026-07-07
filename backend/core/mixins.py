"""Mixins reutilizáveis para modelos e views."""

from django.db import models


class TimestampMixin(models.Model):
    created_at = models.DateTimeField("Criado em", auto_now_add=True)
    updated_at = models.DateTimeField("Atualizado em", auto_now=True)

    class Meta:
        abstract = True


class SoftDeleteMixin(models.Model):
    is_deleted = models.BooleanField("Eliminado", default=False)
    deleted_at = models.DateTimeField("Eliminado em", null=True, blank=True)

    class Meta:
        abstract = True
