"""Invalidação de cache do módulo de laboratório."""

from django.core.cache import cache

from apps.laboratory.constants import CACHE_KEY_LAB_RESULTS, CACHE_KEY_LAB_SUMMARY


class LaboratoryCacheService:
    @staticmethod
    def invalidate_all(*, patient_id: int | None = None, consulta_id: int | None = None) -> None:
        cache.delete(CACHE_KEY_LAB_SUMMARY)
        cache.delete(CACHE_KEY_LAB_RESULTS)
        if patient_id:
            cache.delete(f"sgcs:patient:{patient_id}:clinical")
        if consulta_id:
            cache.delete(f"sgcs:consulta:{consulta_id}:clinical")
        cache.delete("sgcs:dashboard:clinical")
        cache.delete("sgcs:dashboard:laboratory")
