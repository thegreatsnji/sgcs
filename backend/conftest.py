"""Fixtures partilhadas de testes."""

import pytest
from django.contrib.auth import get_user_model

from apps.authentication.models import UserRole
from apps.users.management.commands.seed_rbac import Command as SeedRBACCommand

User = get_user_model()


@pytest.fixture(autouse=True)
def seed_rbac(db):
    SeedRBACCommand().handle()


@pytest.fixture(autouse=True)
def use_locmem_cache(settings):
    settings.USE_REDIS = False
    settings.CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "pytest",
        }
    }


@pytest.fixture
def api_client():
    from rest_framework.test import APIClient

    return APIClient()


@pytest.fixture
def admin_user(db):
    return User.objects.create_user(
        email="admin@test.gw",
        password="Admin@12345",
        first_name="Admin",
        last_name="Teste",
        role=UserRole.ADMINISTRADOR,
        is_staff=True,
    )


@pytest.fixture
def receptionist_user(db):
    return User.objects.create_user(
        email="rececao@test.gw",
        password="Rececao@123",
        first_name="Receção",
        last_name="Teste",
        role=UserRole.RECECIONISTA,
    )
