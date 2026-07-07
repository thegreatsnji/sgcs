"""Cache Redis para configurações."""

from django.core.cache import cache

from apps.settings.constants import CACHE_KEY_CLINIC, CACHE_KEY_SETTINGS_PREFIX, CACHE_KEY_SYSTEM_DASHBOARD, CACHE_TTL


class SettingsCacheService:
    @staticmethod
    def get_clinic():
        return cache.get(CACHE_KEY_CLINIC)

    @staticmethod
    def set_clinic(data: dict) -> None:
        cache.set(CACHE_KEY_CLINIC, data, CACHE_TTL)

    @staticmethod
    def get_system_dashboard():
        return cache.get(CACHE_KEY_SYSTEM_DASHBOARD)

    @staticmethod
    def set_system_dashboard(data: dict) -> None:
        cache.set(CACHE_KEY_SYSTEM_DASHBOARD, data, CACHE_TTL)

    @staticmethod
    def invalidate_all() -> None:
        cache.delete(CACHE_KEY_CLINIC)
        cache.delete(CACHE_KEY_SYSTEM_DASHBOARD)

    @staticmethod
    def invalidate_key(key: str) -> None:
        cache.delete(CACHE_KEY_SETTINGS_PREFIX.format(key=key))
