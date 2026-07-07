"""Cache Redis do módulo financeiro."""

from django.core.cache import cache

from apps.finance.constants import CACHE_KEY_CASHFLOW, CACHE_KEY_DASHBOARD, CACHE_KEY_REPORT, CACHE_TTL


class FinanceCacheService:
    @staticmethod
    def invalidate_all() -> None:
        cache.delete(CACHE_KEY_DASHBOARD)
        cache.delete(CACHE_KEY_CASHFLOW)

    @staticmethod
    def get_dashboard():
        return cache.get(CACHE_KEY_DASHBOARD)

    @staticmethod
    def set_dashboard(data: dict) -> None:
        cache.set(CACHE_KEY_DASHBOARD, data, CACHE_TTL)

    @staticmethod
    def get_report(tipo: str, periodo: str):
        return cache.get(CACHE_KEY_REPORT.format(tipo=tipo, periodo=periodo))

    @staticmethod
    def set_report(tipo: str, periodo: str, data: dict) -> None:
        cache.set(CACHE_KEY_REPORT.format(tipo=tipo, periodo=periodo), data, CACHE_TTL)
