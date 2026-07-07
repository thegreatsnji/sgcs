"""Configuração central do núcleo SGCS."""

from core.config.cache import build_cache_config, build_fallback_cache_config
from core.config.constants import APP_CODE, APP_VERSION
from core.config.enums import CacheBackend, Environment, StorageBackend
from core.config.feature_flags import get_feature_flags, is_feature_enabled
from core.config.storage import get_media_root, get_media_url, get_storage_backend, get_upload_paths

__all__ = [
    "APP_CODE",
    "APP_VERSION",
    "CacheBackend",
    "Environment",
    "StorageBackend",
    "build_cache_config",
    "build_fallback_cache_config",
    "get_feature_flags",
    "get_media_root",
    "get_media_url",
    "get_storage_backend",
    "get_upload_paths",
    "is_feature_enabled",
]
