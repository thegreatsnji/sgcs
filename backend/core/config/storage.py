"""Configuração de armazenamento de ficheiros."""

import os
from pathlib import Path

from core.config.enums import StorageBackend


def get_storage_backend() -> str:
    return os.getenv("STORAGE_BACKEND", StorageBackend.LOCAL)


def get_media_root(base_dir: Path) -> Path:
    return base_dir / "media"


def get_media_url() -> str:
    return os.getenv("MEDIA_URL", "/media/")


def get_upload_paths() -> dict[str, str]:
    return {
        "users": "users/photos/",
        "documents": "documents/",
        "images": "images/",
        "exports": "exports/",
    }
