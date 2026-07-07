"""Testes de auditoria."""

import pytest
from rest_framework import status

from apps.audit_logs.models import AuditAction, AuditLog


@pytest.mark.django_db
class TestAudit:
    def test_login_creates_audit_log(self, api_client, admin_user):
        response = api_client.post(
            "/api/v1/auth/login/",
            {"email": admin_user.email, "password": "Admin@12345"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert AuditLog.objects.filter(action=AuditAction.LOGIN, user=admin_user).exists()

    def test_admin_can_list_audit_logs(self, api_client, admin_user):
        api_client.force_authenticate(user=admin_user)
        response = api_client.get("/api/v1/audit-logs/")
        assert response.status_code == status.HTTP_200_OK
