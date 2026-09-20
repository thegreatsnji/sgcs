"""Contrato RBAC: Receção não acede a módulos clínicos/admin indevidos; bridge lab billing OK."""

import pytest
from rest_framework import status

from apps.authentication.models import UserRole
from apps.users.services.rbac_service import RBACService


FORBIDDEN_FOR_RECEPTION = (
    "laboratory.view",
    "laboratory.results.view",
    "laboratory.results.validate",
    "pharmacy.view",
    "stock.view",
    "stock.adjust",
    "appointments.clinical",
    "appointments.diagnosis",
    "doctors.prescription",
    "settings.edit",
    "users.view",
)


@pytest.mark.django_db
class TestReceptionRbacVisibilityContract:
    def test_receptionist_lacks_clinical_admin_permissions(self, receptionist_user, seed_rbac):
        perms = set(RBACService.get_user_permissions(receptionist_user))
        for codename in FORBIDDEN_FOR_RECEPTION:
            assert codename not in perms, f"Receção não deve ter {codename}"

    def test_receptionist_has_operational_billing_and_lab_bridge(
        self, receptionist_user, seed_rbac
    ):
        perms = set(RBACService.get_user_permissions(receptionist_user))
        for codename in (
            "reception.view",
            "reception.create",
            "reception.edit",
            "billing.view",
            "billing.create",
            "billing.payment",
            "billing.receipt",
        ):
            assert codename in perms, f"Receção deve ter {codename}"
        assert "billing.quote" not in perms
        assert "billing.delete" not in perms

    def test_lab_clinical_api_forbidden(self, api_client, receptionist_user, seed_rbac):
        api_client.force_authenticate(user=receptionist_user)
        assert api_client.get("/api/v1/laboratory/").status_code == status.HTTP_403_FORBIDDEN

    def test_stock_api_forbidden(self, api_client, receptionist_user, seed_rbac):
        api_client.force_authenticate(user=receptionist_user)
        r = api_client.get("/api/v1/pharmacy/urgent-medicines/")
        assert r.status_code == status.HTTP_403_FORBIDDEN
        r2 = api_client.get("/api/v1/stock/items/")
        assert r2.status_code == status.HTTP_403_FORBIDDEN

    def test_pending_lab_orders_bridge_ok(self, api_client, receptionist_user, seed_rbac):
        api_client.force_authenticate(user=receptionist_user)
        r = api_client.get("/api/v1/reception/pending-clinical-lab-orders/")
        assert r.status_code == status.HTTP_200_OK

    def test_service_catalog_write_forbidden(self, api_client, receptionist_user, seed_rbac):
        api_client.force_authenticate(user=receptionist_user)
        r = api_client.post(
            "/api/v1/billing/services/",
            {"codigo": "X", "nome": "Y", "categoria": "CONSULTA", "preco": "100"},
            format="json",
        )
        assert r.status_code == status.HTTP_403_FORBIDDEN

    def test_lab_role_keeps_laboratory(self, api_client, seed_rbac, db):
        from django.contrib.auth import get_user_model

        User = get_user_model()
        lab = User.objects.create_user(
            email="lab.rbac@test.gw",
            password="Lab@12345",
            first_name="Lab",
            last_name="User",
            role=UserRole.LABORATORIO,
        )
        api_client.force_authenticate(user=lab)
        # May be 200 or empty list depending on view; must not be 403 if they have laboratory.view
        perms = set(RBACService.get_user_permissions(lab))
        assert "laboratory.view" in perms

    def test_nurse_keeps_stock_permission(self, seed_rbac, db):
        from django.contrib.auth import get_user_model

        User = get_user_model()
        nurse = User.objects.create_user(
            email="enf.rbac@test.gw",
            password="Enf@12345",
            first_name="Enf",
            last_name="User",
            role=UserRole.ENFERMEIRO,
        )
        perms = set(RBACService.get_user_permissions(nurse))
        assert "stock.view" in perms or "pharmacy.view" in perms

    def test_director_read_only_billing(self, seed_rbac, db):
        from django.contrib.auth import get_user_model

        User = get_user_model()
        director = User.objects.create_user(
            email="dir.rbac@test.gw",
            password="Dir@12345",
            first_name="Dir",
            last_name="User",
            role=UserRole.DIRECTOR,
        )
        perms = set(RBACService.get_user_permissions(director))
        assert "billing.view" in perms
        assert "billing.create" not in perms
        assert "stock.view" in perms
        assert "stock.adjust" not in perms
