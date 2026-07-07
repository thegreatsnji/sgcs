"""Testes dos endpoints de saúde."""

import pytest


@pytest.mark.django_db
def test_health_endpoint(client):
    response = client.get("/health/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["app"] == "SGCS"


def test_live_endpoint(client):
    response = client.get("/live/")
    assert response.status_code == 200
    assert response.json()["status"] == "alive"


@pytest.mark.django_db
def test_ready_endpoint(client, settings):
    settings.USE_REDIS = False
    settings.CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "test-ready",
        }
    }
    response = client.get("/ready/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert data["checks"]["database"]["ok"] is True
    assert data["checks"]["redis"]["ok"] is True
