"""Modelos de ficheiros e documentos."""

from django.conf import settings
from django.db import models


class StoredFile(models.Model):
    name = models.CharField("Nome", max_length=255)
    file = models.FileField("Ficheiro", upload_to="documents/")
    mime_type = models.CharField("Tipo MIME", max_length=100, blank=True)
    size = models.PositiveIntegerField("Tamanho (bytes)", default=0)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="uploaded_files",
        verbose_name="Carregado por",
    )
    created_at = models.DateTimeField("Criado em", auto_now_add=True)

    class Meta:
        verbose_name = "Ficheiro"
        verbose_name_plural = "Ficheiros"
        ordering = ["-created_at"]
