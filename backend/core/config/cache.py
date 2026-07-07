"""Configuração de cache do SGCS."""

import os


def build_cache_config() -> dict:
    redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")

    return {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": redis_url,
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
            },
            "KEY_PREFIX": "sgcs",
            "TIMEOUT": int(os.getenv("CACHE_TIMEOUT", "300")),
        }
    }


def build_fallback_cache_config() -> dict:
    return {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "sgcs-fallback",
        }
    }
