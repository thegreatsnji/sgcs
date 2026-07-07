"""Validação de uploads de ficheiros."""

import os

from django.core.exceptions import ValidationError

MAX_UPLOAD_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", "10"))
MAX_UPLOAD_BYTES = MAX_UPLOAD_SIZE_MB * 1024 * 1024

ALLOWED_MIME_TYPES = {
    mime.strip()
    for mime in os.getenv(
        "ALLOWED_UPLOAD_MIME_TYPES",
        "image/jpeg,image/png,image/webp,application/pdf,"
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,"
        "text/csv",
    ).split(",")
    if mime.strip()
}


def validate_upload(file) -> None:
    if file.size > MAX_UPLOAD_BYTES:
        raise ValidationError(
            f"Ficheiro demasiado grande. Limite: {MAX_UPLOAD_SIZE_MB} MB."
        )
    content_type = getattr(file, "content_type", "") or ""
    if content_type and content_type not in ALLOWED_MIME_TYPES:
        raise ValidationError(f"Tipo de ficheiro não permitido: {content_type}")
