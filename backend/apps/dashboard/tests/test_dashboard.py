"""Testes do dashboard clínico e administrativo."""

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status

from apps.authentication.models import UserRole
from apps.patients.services.patient_service import PatientService

User = get_user_model()


@pytest.fixture
def doctor_user(db):
    return User.objects.create_user(
        email="medico@test.gw",
        password="Medico@123",
        first_name="Paulo",
        last_name="Médico",
        role=UserRole.MEDICO,
    )


@pytest.fixture
def patient(db, receptionist_user):
    return PatientService.create(
        {
            "first_name": "Ana",
            "last_name": "Costa",
            "birth_date": __import__("datetime").date(1990, 3, 15),
            "gender": "F",
            "phone": "+245955111222",
            "document_number": "DOC-DASH",
            "document_type": "BI",
        },
        user=receptionist_user,
        emergency_contacts=[
            {
                "name": "Contacto",
                "phone": "+245955333444",
                "relationship": "CONJUGE",
                "is_primary": True,
            }
        ],
    )


@pytest.mark.django_db
class TestDashboardIntegration:
    def test_clinical_summary_requires_patients_view(self, api_client, doctor_user):
        api_client.force_authenticate(user=doctor_user)
        response = api_client.get("/api/v1/dashboard/clinical/")
        assert response.status_code == status.HTTP_200_OK
        assert "total_patients" in response.data["data"]["cards"]

    def test_admin_summary_includes_patient_cards(self, api_client, admin_user, patient):
        api_client.force_authenticate(user=admin_user)
        response = api_client.get("/api/v1/dashboard/admin/")
        assert response.status_code == status.HTTP_200_OK
        cards = response.data["data"]["cards"]
        assert cards["total_patients"] >= 1
        assert "recent_patient_activity" in response.data["data"]
