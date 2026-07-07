"""Cache Redis para histórico clínico."""

from django.core.cache import cache

from apps.doctors.constants import CACHE_KEY_HISTORICO, CACHE_TTL


class DoctorsCacheService:
    @staticmethod
    def get_historico(paciente_id: int):
        return cache.get(CACHE_KEY_HISTORICO.format(paciente_id=paciente_id))

    @staticmethod
    def set_historico(paciente_id: int, data: dict) -> None:
        cache.set(CACHE_KEY_HISTORICO.format(paciente_id=paciente_id), data, CACHE_TTL)

    @staticmethod
    def invalidate_historico(paciente_id: int) -> None:
        cache.delete(CACHE_KEY_HISTORICO.format(paciente_id=paciente_id))
