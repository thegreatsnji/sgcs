"""Invalidação de cache do módulo de faturação."""

from django.core.cache import cache

from apps.billing.constants import CACHE_KEY_DASHBOARD, CACHE_KEY_PATIENT_HISTORY, CACHE_KEY_SERVICES


class BillingCacheService:
    @staticmethod
    def invalidate_all(*, patient_id: int | None = None) -> None:
        cache.delete(CACHE_KEY_SERVICES)
        cache.delete(CACHE_KEY_DASHBOARD)
        if patient_id:
            cache.delete(CACHE_KEY_PATIENT_HISTORY.format(patient_id=patient_id))
