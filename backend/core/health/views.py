"""Endpoints de saúde e prontidão do SGCS."""

from django.conf import settings
from django.http import JsonResponse
from django.views import View

from core.config.constants import APP_CODE, APP_VERSION
from core.monitoring.health_service import HealthService


class HealthView(View):
    """Verificação geral de saúde da aplicação."""

    authentication_classes: list = []
    permission_classes: list = []

    def get(self, request):
        return JsonResponse(
            {
                "status": "ok",
                "app": APP_CODE,
                "version": APP_VERSION,
                "environment": settings.APP_ENV if hasattr(settings, "APP_ENV") else "unknown",
            }
        )


class LiveView(View):
    """Liveness probe — processo em execução."""

    def get(self, request):
        return JsonResponse({"status": "alive"})


class ReadyView(View):
    """Readiness probe — dependências críticas disponíveis."""

    def get(self, request):
        status_payload = HealthService.full_status()
        is_ready = status_payload["status"] == "ready"
        status_code = 200 if is_ready else 503
        return JsonResponse(status_payload, status=status_code)
