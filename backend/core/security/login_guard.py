"""Protecção contra brute-force no login."""

import logging

from django.core.cache import cache

logger = logging.getLogger("core.security")

MAX_ATTEMPTS = 5
LOCKOUT_SECONDS = 900


class LoginGuardService:
    @staticmethod
    def _key(email: str) -> str:
        return f"sgcs:security:login:{email.lower().strip()}"

    @staticmethod
    def is_allowed(email: str) -> bool:
        attempts = cache.get(LoginGuardService._key(email), 0)
        return attempts < MAX_ATTEMPTS

    @staticmethod
    def record_failure(email: str) -> int:
        key = LoginGuardService._key(email)
        attempts = cache.get(key, 0) + 1
        cache.set(key, attempts, LOCKOUT_SECONDS)
        if attempts >= MAX_ATTEMPTS:
            logger.warning("Conta bloqueada por tentativas excessivas: %s", email)
        return attempts

    @staticmethod
    def clear(email: str) -> None:
        cache.delete(LoginGuardService._key(email))

    @staticmethod
    def remaining_lockout_seconds(email: str) -> int:
        if LoginGuardService.is_allowed(email):
            return 0
        return LOCKOUT_SECONDS
