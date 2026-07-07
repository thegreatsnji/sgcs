"""Helper central de cache Redis para o SGCS."""

from __future__ import annotations

import hashlib
import json
import logging
import os
from collections.abc import Callable
from typing import Any, TypeVar

from django.core.cache import cache

logger = logging.getLogger(__name__)

T = TypeVar("T")


class CacheTTL:
    """TTL configurável por domínio (segundos)."""

    DEFAULT = int(os.getenv("CACHE_TIMEOUT", "300"))
    DASHBOARD = int(os.getenv("CACHE_TTL_DASHBOARD", "120"))
    PATIENTS = int(os.getenv("CACHE_TTL_PATIENTS", "120"))
    REPORTS = int(os.getenv("CACHE_TTL_REPORTS", "120"))
    LABORATORY = int(os.getenv("CACHE_TTL_LABORATORY", "120"))
    FINANCE = int(os.getenv("CACHE_TTL_FINANCE", "60"))
    BILLING = int(os.getenv("CACHE_TTL_BILLING", "60"))
    SETTINGS = int(os.getenv("CACHE_TTL_SETTINGS", "300"))
    EXECUTIVE = int(os.getenv("CACHE_TTL_EXECUTIVE", "120"))


class CacheHelper:
  PREFIX = "sgcs"

  @staticmethod
  def build_key(namespace: str, key: str) -> str:
      return f"{CacheHelper.PREFIX}:{namespace}:{key}"

  @staticmethod
  def get_or_set(
      namespace: str,
      key: str,
      factory: Callable[[], T],
      ttl: int | None = None,
  ) -> T:
      full_key = CacheHelper.build_key(namespace, key)
      cached = cache.get(full_key)
      if cached is not None:
          return cached
      value = factory()
      cache.set(full_key, value, ttl or CacheTTL.DEFAULT)
      return value

  @staticmethod
  def get(namespace: str, key: str) -> Any:
      return cache.get(CacheHelper.build_key(namespace, key))

  @staticmethod
  def set(namespace: str, key: str, value: Any, ttl: int | None = None) -> None:
      cache.set(CacheHelper.build_key(namespace, key), value, ttl or CacheTTL.DEFAULT)

  @staticmethod
  def delete(namespace: str, key: str) -> None:
      cache.delete(CacheHelper.build_key(namespace, key))

  @staticmethod
  def invalidate_namespace(namespace: str, keys: list[str]) -> None:
      for key in keys:
          CacheHelper.delete(namespace, key)
      logger.debug("Cache invalidado: namespace=%s keys=%s", namespace, keys)

  @staticmethod
  def hash_params(params: dict) -> str:
      payload = json.dumps(params, sort_keys=True, default=str)
      return hashlib.md5(payload.encode()).hexdigest()[:16]
