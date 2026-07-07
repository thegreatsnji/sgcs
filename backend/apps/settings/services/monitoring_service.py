"""Monitorização do sistema."""

import os
import shutil
from pathlib import Path

from django.conf import settings as django_settings
from django.core.cache import cache
from django.db import connection

from core.config.constants import APP_VERSION
from core.config.feature_flags import get_feature_flags
from core.monitoring.health_service import HealthService


class MonitoringService:
    @staticmethod
    def get_system_status() -> dict:
        return {
            "versao": APP_VERSION,
            "ambiente": getattr(django_settings, "APP_ENV", "development"),
            "health": MonitoringService._health_summary(),
            "database": MonitoringService._check_database(),
            "redis": MonitoringService._check_redis(),
            "celery": HealthService.check_celery(),
            "disco": MonitoringService._disk_usage(),
            "memoria": MonitoringService._memory_usage(),
            "cpu": MonitoringService._cpu_usage(),
            "utilizadores": MonitoringService._user_counts(),
            "sessoes": MonitoringService._session_count(),
            "feature_flags": get_feature_flags(),
        }

    @staticmethod
    def _health_summary() -> str:
        checks = [
            MonitoringService._check_database()["ok"],
            MonitoringService._check_redis()["ok"],
        ]
        return "ok" if all(checks) else "degraded"

    @staticmethod
    def _check_database() -> dict:
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            return {"ok": True, "status": "conectado"}
        except Exception as exc:
            return {"ok": False, "status": "erro", "detalhe": str(exc)}

    @staticmethod
    def _check_redis() -> dict:
        try:
            cache.set("sgcs:monitor:probe", "1", 5)
            ok = cache.get("sgcs:monitor:probe") == "1"
            return {"ok": ok, "status": "conectado" if ok else "indisponível"}
        except Exception as exc:
            return {"ok": False, "status": "erro", "detalhe": str(exc)}

    @staticmethod
    def _disk_usage() -> dict:
        try:
            base = Path(getattr(django_settings, "BASE_DIR", "."))
            usage = shutil.disk_usage(base)
            return {
                "total_gb": round(usage.total / (1024**3), 2),
                "usado_gb": round(usage.used / (1024**3), 2),
                "livre_gb": round(usage.free / (1024**3), 2),
            }
        except Exception:
            return {"total_gb": 0, "usado_gb": 0, "livre_gb": 0}

    @staticmethod
    def _memory_usage() -> dict:
        try:
            import resource

            usage = resource.getrusage(resource.RUSAGE_SELF)
            return {"rss_mb": round(usage.ru_maxrss / 1024, 2)}
        except Exception:
            return {"rss_mb": 0}

    @staticmethod
    def _cpu_usage() -> dict:
        try:
            load = os.getloadavg()
            return {"load_1m": round(load[0], 2), "load_5m": round(load[1], 2)}
        except (AttributeError, OSError):
            return {"load_1m": 0, "load_5m": 0}

    @staticmethod
    def _user_counts() -> dict:
        from apps.authentication.models import User

        total = User.objects.count()
        activos = User.objects.filter(is_active=True).count()
        return {"total": total, "activos": activos}

    @staticmethod
    def _session_count() -> int:
        try:
            from django.contrib.sessions.models import Session

            return Session.objects.count()
        except Exception:
            return 0
