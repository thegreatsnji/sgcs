"""Serviço de armazenamento abstracto (filesystem, S3, MinIO, Azure)."""

import os
from pathlib import Path

from django.conf import settings
from django.core.files.storage import default_storage

from core.config.enums import StorageBackend


class StorageService:
    @staticmethod
    def get_backend() -> str:
        return os.getenv("STORAGE_BACKEND", StorageBackend.LOCAL)

    @staticmethod
    def save(path: str, content) -> str:
        return default_storage.save(path, content)

    @staticmethod
    def delete(path: str) -> None:
        if default_storage.exists(path):
            default_storage.delete(path)

    @staticmethod
    def url(path: str) -> str:
        return default_storage.url(path)

    @staticmethod
    def get_config() -> dict:
        backend = StorageService.get_backend()
        config = {
            "backend": backend,
            "media_url": getattr(settings, "MEDIA_URL", "/media/"),
            "media_root": str(getattr(settings, "MEDIA_ROOT", "")),
        }
        if backend in (StorageBackend.S3, "s3", "minio"):
            config.update(
                {
                    "bucket": os.getenv("AWS_STORAGE_BUCKET_NAME", ""),
                    "endpoint": os.getenv("AWS_S3_ENDPOINT_URL", ""),
                }
            )
        if backend in ("azure", "azureblob"):
            config.update({"account": os.getenv("AZURE_ACCOUNT_NAME", "")})
        return config

    @staticmethod
    def ensure_local_dirs() -> None:
        media_root = Path(getattr(settings, "MEDIA_ROOT", settings.BASE_DIR / "media"))
        for sub in ("users/photos", "documents", "images", "exports"):
            (media_root / sub).mkdir(parents=True, exist_ok=True)
