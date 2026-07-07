"""Testes do módulo de utilizadores."""

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status

from apps.authentication.models import UserRole

User = get_user_model()


@pytest.mark.django_db
class TestUserCRUD:
    def test_admin_can_list_users(self, api_client, admin_user):
        api_client.force_authenticate(user=admin_user)
        response = api_client.get("/api/v1/users/accounts/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True

    def test_admin_can_create_user(self, api_client, admin_user):
        api_client.force_authenticate(user=admin_user)
        payload = {
            "email": "novo@test.gw",
            "first_name": "Novo",
            "last_name": "Utilizador",
            "role": UserRole.RECECIONISTA,
            "password": "Novo@1234",
            "password_confirm": "Novo@1234",
        }
        response = api_client.post("/api/v1/users/accounts/", payload, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.filter(email="novo@test.gw").exists()

    def test_cannot_delete_last_admin(self, api_client, admin_user):
        api_client.force_authenticate(user=admin_user)
        response = api_client.delete(f"/api/v1/users/accounts/{admin_user.pk}/")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_soft_delete_user(self, api_client, admin_user, receptionist_user):
        api_client.force_authenticate(user=admin_user)
        response = api_client.delete(f"/api/v1/users/accounts/{receptionist_user.pk}/")
        assert response.status_code == status.HTTP_200_OK
        receptionist_user.refresh_from_db()
        assert receptionist_user.deleted_at is not None


@pytest.mark.django_db
class TestRBAC:
    def test_receptionist_cannot_create_users_without_permission(self, api_client, receptionist_user):
        api_client.force_authenticate(user=receptionist_user)
        response = api_client.get("/api/v1/users/accounts/")
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestProfile:
    def test_user_can_view_profile(self, api_client, admin_user):
        api_client.force_authenticate(user=admin_user)
        response = api_client.get("/api/v1/users/profile/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["data"]["email"] == admin_user.email
