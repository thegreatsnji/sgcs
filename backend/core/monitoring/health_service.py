"""Monitorização e health checks avançados."""

import os
import shutil
import time
from pathlib import Path

from django.conf import settings
from django.core.cache import cache
from django.db import connection


class HealthService:
    @staticmethod
    def full_status() -> dict:
        db = HealthService.check_database()
        redis = HealthService.check_redis()
        celery = HealthService.check_celery()
        checks = {
            "database": db,
            "redis": redis,
            "celery": celery,
            "disco": HealthService.check_disk(),
            "memoria": HealthService.check_memory(),
            "cpu": HealthService.check_cpu(),
        }
        critical_ok = db["ok"] and redis["ok"]
        return {
            "status": "ready" if critical_ok else "not_ready",
            "checks": checks,
            "fila_celery": celery.get("fila_pendente", 0),
            "workers": celery.get("workers", 0),
            "tempo_resposta_db_ms": db.get("latencia_ms", 0),
        }

    @staticmethod
    def check_database() -> dict:
        start = time.perf_counter()
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            latency = round((time.perf_counter() - start) * 1000, 2)
            return {"ok": True, "status": "conectado", "latencia_ms": latency}
        except Exception as exc:
            return {"ok": False, "status": "erro", "detalhe": str(exc), "latencia_ms": 0}

    @staticmethod
    def check_redis() -> dict:
        try:
            cache.set("sgcs:health:probe", "1", 5)
            ok = cache.get("sgcs:health:probe") == "1"
            return {"ok": ok, "status": "conectado" if ok else "indisponível"}
        except Exception as exc:
            return {"ok": False, "status": "erro", "detalhe": str(exc)}

    @staticmethod
    def check_celery() -> dict:
        try:
            from config.celery import app

            inspect = app.control.inspect(timeout=1.0)
            stats = inspect.stats() or {}
            active = inspect.active() or {}
            workers = len(stats)
            fila = sum(len(tasks) for tasks in active.values())
            return {
                "ok": workers > 0 or os.getenv("CELERY_OPTIONAL", "true").lower() == "true",
                "status": "activo" if workers else "sem_workers",
                "workers": workers,
                "fila_pendente": fila,
            }
        except Exception as exc:
            return {
                "ok": os.getenv("CELERY_OPTIONAL", "true").lower() == "true",
                "status": "indisponível",
                "detalhe": str(exc),
                "workers": 0,
                "fila_pendente": 0,
            }

    @staticmethod
    def check_disk() -> dict:
        try:
            base = Path(getattr(settings, "BASE_DIR", "."))
            usage = shutil.disk_usage(base)
            return {
                "ok": usage.free > 100 * 1024 * 1024,
                "total_gb": round(usage.total / (1024**3), 2),
                "usado_gb": round(usage.used / (1024**3), 2),
                "livre_gb": round(usage.free / (1024**3), 2),
            }
        except Exception:
            return {"ok": False, "total_gb": 0, "usado_gb": 0, "livre_gb": 0}

    @staticmethod
    def check_memory() -> dict:
        try:
            import resource

            usage = resource.getrusage(resource.RUSAGE_SELF)
            rss_mb = round(usage.ru_maxrss / 1024, 2)
            return {"ok": True, "rss_mb": rss_mb}
        except Exception:
            return {"ok": True, "rss_mb": 0}

    @staticmethod
    def check_cpu() -> dict:
        try:
            import resource

            usage = resource.getrusage(resource.RUSAGE_SELF)
            return {"ok": True, "user_time_s": round(usage.ru_utime, 2)}
        except Exception:
            return {"ok": True, "user_time_s": 0}
