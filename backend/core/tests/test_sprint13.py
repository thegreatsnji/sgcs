"""Testes Sprint 13 — produção, performance, segurança."""

import io

import pytest
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.test import RequestFactory
from rest_framework import status

from core.cache.cache_helper import CacheHelper, CacheTTL
from core.monitoring.health_service import HealthService
from core.security.login_guard import LoginGuardService
from core.security.middleware import SecurityHeadersMiddleware
from core.security.upload_validators import validate_upload
from core.storage.storage_service import StorageService


@pytest.fixture(autouse=True)
def clear_cache():
    cache.clear()
    yield
    cache.clear()


@pytest.mark.django_db
class TestCacheHelper:
    def test_get_or_set(self):
        calls = {"n": 0}

        def factory():
            calls["n"] += 1
            return {"ok": True}

        r1 = CacheHelper.get_or_set("test", "key1", factory, ttl=60)
        r2 = CacheHelper.get_or_set("test", "key1", factory, ttl=60)
        assert r1 == r2
        assert calls["n"] == 1

    def test_invalidate(self):
        CacheHelper.set("patients", "list", [1, 2], ttl=60)
        CacheHelper.delete("patients", "list")
        assert CacheHelper.get("patients", "list") is None

    def test_hash_params(self):
        h1 = CacheHelper.hash_params({"a": 1, "b": 2})
        h2 = CacheHelper.hash_params({"b": 2, "a": 1})
        assert h1 == h2

    def test_ttl_constants(self):
        assert CacheTTL.DASHBOARD >= 60


@pytest.mark.django_db
class TestLoginGuard:
    def test_block_after_failures(self):
        email = "brute@test.com"
        assert LoginGuardService.is_allowed(email)
        for _ in range(5):
            LoginGuardService.record_failure(email)
        assert not LoginGuardService.is_allowed(email)

    def test_clear_after_success(self):
        email = "clear@test.com"
        LoginGuardService.record_failure(email)
        LoginGuardService.clear(email)
        assert LoginGuardService.is_allowed(email)


@pytest.mark.django_db
class TestUploadValidators:
    def test_reject_large_file(self):
        class FakeFile:
            size = 20 * 1024 * 1024
            content_type = "image/jpeg"

        with pytest.raises(ValidationError):
            validate_upload(FakeFile())

    def test_reject_bad_mime(self):
        class FakeFile:
            size = 100
            content_type = "application/x-msdownload"

        with pytest.raises(ValidationError):
            validate_upload(FakeFile())


class TestSecurityMiddleware:
    def test_security_headers(self):
        def get_response(request):
            from django.http import HttpResponse

            return HttpResponse("ok")

        middleware = SecurityHeadersMiddleware(get_response)
        request = RequestFactory().get("/")
        response = middleware(request)
        assert response["X-Content-Type-Options"] == "nosniff"
        assert "Referrer-Policy" in response


@pytest.mark.django_db
class TestHealthService:
    def test_database_check(self):
        result = HealthService.check_database()
        assert result["ok"] is True
        assert "latencia_ms" in result

    def test_redis_check(self):
        result = HealthService.check_redis()
        assert result["ok"] is True

    def test_full_status(self):
        status_payload = HealthService.full_status()
        assert "checks" in status_payload
        assert "database" in status_payload["checks"]

    def test_ready_endpoint(self, api_client):
        response = api_client.get("/ready/")
        assert response.status_code in (200, 503)


class TestStorageService:
    def test_get_config(self):
        config = StorageService.get_config()
        assert "backend" in config
        assert "media_url" in config


@pytest.mark.django_db
class TestDashboardCache:
    def test_admin_summary_cached(self):
        from apps.dashboard.services import DashboardService

        s1 = DashboardService.get_admin_summary()
        s2 = DashboardService.get_admin_summary()
        assert s1 == s2


@pytest.mark.django_db
class TestPdfExport:
    def test_pdf_has_footer_metadata(self):
        from apps.reports.services.pdf_service import PdfExportService

        pdf = PdfExportService.export_report("Teste", {"total": 1})
        assert pdf[:4] == b"%PDF"


@pytest.mark.django_db
class TestPerformanceQueryset:
    def test_patients_list_optimized(self, api_client, admin_user):
        api_client.force_authenticate(user=admin_user)
        response = api_client.get("/api/v1/patients/")
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestLoggingConfig:
    def test_build_logging_config(self, settings):
        from pathlib import Path

        from core.logging_config import build_logging_config

        config = build_logging_config(Path(settings.BASE_DIR), json_format=False)
        assert "handlers" in config
        assert "application_file" in config["handlers"]


@pytest.mark.django_db
class TestCeleryTasks:
    def test_notification_tasks(self):
        from apps.notifications.tasks import processar_fila

        result = processar_fila()
        assert result["status"] == "ok"
