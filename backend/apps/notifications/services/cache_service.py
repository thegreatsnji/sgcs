"""Cache Redis para notificações."""

from django.core.cache import cache

from apps.notifications.constants import (
    CACHE_KEY_CONTADOR,
    CACHE_KEY_DASHBOARD,
    CACHE_KEY_NAO_LIDAS,
    CACHE_TTL,
)


class NotificationCacheService:
    @staticmethod
    def invalidate_user(user_id: int) -> None:
        cache.delete(CACHE_KEY_NAO_LIDAS.format(user_id=user_id))
        cache.delete(CACHE_KEY_CONTADOR.format(user_id=user_id))

    @staticmethod
    def invalidate_dashboard() -> None:
        cache.delete(CACHE_KEY_DASHBOARD)

    @staticmethod
    def get_nao_lidas(user_id: int):
        return cache.get(CACHE_KEY_NAO_LIDAS.format(user_id=user_id))

    @staticmethod
    def set_nao_lidas(user_id: int, data: list) -> None:
        cache.set(CACHE_KEY_NAO_LIDAS.format(user_id=user_id), data, CACHE_TTL)

    @staticmethod
    def get_contador(user_id: int) -> int | None:
        return cache.get(CACHE_KEY_CONTADOR.format(user_id=user_id))

    @staticmethod
    def set_contador(user_id: int, count: int) -> None:
        cache.set(CACHE_KEY_CONTADOR.format(user_id=user_id), count, CACHE_TTL)

    @staticmethod
    def get_dashboard():
        return cache.get(CACHE_KEY_DASHBOARD)

    @staticmethod
    def set_dashboard(data: dict) -> None:
        cache.set(CACHE_KEY_DASHBOARD, data, CACHE_TTL)
