"""Cache Redis para relatórios e BI."""

from django.core.cache import cache

from apps.reports.constants import (
    CACHE_KEY_CHARTS,
    CACHE_KEY_EXECUTIVE,
    CACHE_KEY_REPORT,
    CACHE_KEY_STATISTICS,
    CACHE_TTL,
)


class ReportsCacheService:
    @staticmethod
    def get_report(tipo: str, periodo: str, filtros_hash: str):
        return cache.get(CACHE_KEY_REPORT.format(tipo=tipo, periodo=periodo, filtros_hash=filtros_hash))

    @staticmethod
    def set_report(tipo: str, periodo: str, filtros_hash: str, data: dict) -> None:
        cache.set(
            CACHE_KEY_REPORT.format(tipo=tipo, periodo=periodo, filtros_hash=filtros_hash),
            data,
            CACHE_TTL,
        )

    @staticmethod
    def get_executive():
        return cache.get(CACHE_KEY_EXECUTIVE)

    @staticmethod
    def set_executive(data: dict) -> None:
        cache.set(CACHE_KEY_EXECUTIVE, data, CACHE_TTL)

    @staticmethod
    def get_statistics(tipo: str):
        return cache.get(CACHE_KEY_STATISTICS.format(tipo=tipo))

    @staticmethod
    def set_statistics(tipo: str, data: dict) -> None:
        cache.set(CACHE_KEY_STATISTICS.format(tipo=tipo), data, CACHE_TTL)

    @staticmethod
    def get_charts(serie: str):
        return cache.get(CACHE_KEY_CHARTS.format(serie=serie))

    @staticmethod
    def set_charts(serie: str, data: dict) -> None:
        cache.set(CACHE_KEY_CHARTS.format(serie=serie), data, CACHE_TTL)

    @staticmethod
    def invalidate_all() -> None:
        cache.delete(CACHE_KEY_EXECUTIVE)
