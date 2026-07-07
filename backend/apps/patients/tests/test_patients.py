"""Testes do módulo de pacientes."""

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status

from apps.audit_logs.models import AuditAction, AuditLog
from apps.authentication.models import UserRole
from apps.patients.models import Patient, PatientAllergy, PatientHistory

User = get_user_model()

PATIENT_PAYLOAD = {
    "first_name": "Maria",
    "last_name": "Mendes",
    "document_type": "BI",
    "document_number": "123456789LA045",
    "birth_date": "15/03/1990",
    "gender": "F",
    "phone": "+245955123456",
    "email": "maria.mendes@email.com",
    "emergency_contacts": [
        {
            "name": "João Mendes",
            "phone": "+245955654321",
            "relationship": "CONJUGE",
            "is_primary": True,
        }
    ],
}


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
    from apps.patients.services.patient_service import PatientService

    return PatientService.create(
        {
            "first_name": "Ana",
            "last_name": "Costa",
            "birth_date": __import__("datetime").date(1990, 3, 15),
            "gender": "F",
            "phone": "+245955111222",
            "document_number": "DOC001",
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
class TestPatientCRUD:
    def test_receptionist_can_list_patients(self, api_client, receptionist_user, patient):
        api_client.force_authenticate(user=receptionist_user)
        response = api_client.get("/api/v1/patients/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True
        assert response.data["data"]["count"] >= 1

    def test_receptionist_can_create_patient(self, api_client, receptionist_user):
        api_client.force_authenticate(user=receptionist_user)
        response = api_client.post("/api/v1/patients/", PATIENT_PAYLOAD, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["success"] is True
        assert Patient.objects.filter(document_number="123456789LA045").exists()
        assert AuditLog.objects.filter(action=AuditAction.PATIENT_CREATE).exists()
        assert PatientHistory.objects.filter(event_type="REGISTO").exists()

    def test_duplicate_document_rejected(self, api_client, receptionist_user, patient):
        api_client.force_authenticate(user=receptionist_user)
        payload = {**PATIENT_PAYLOAD, "document_number": "DOC001"}
        response = api_client.post("/api/v1/patients/", payload, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_retrieve_patient(self, api_client, receptionist_user, patient):
        api_client.force_authenticate(user=receptionist_user)
        response = api_client.get(f"/api/v1/patients/{patient.pk}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["data"]["patient_number"].startswith("PAC-")

    def test_update_patient(self, api_client, receptionist_user, patient):
        api_client.force_authenticate(user=receptionist_user)
        response = api_client.patch(
            f"/api/v1/patients/{patient.pk}/",
            {"phone": "+245955999888"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        patient.refresh_from_db()
        assert patient.phone == "+245955999888"
        assert AuditLog.objects.filter(action=AuditAction.PATIENT_UPDATE).exists()

    def test_soft_delete_patient(self, api_client, admin_user, patient):
        api_client.force_authenticate(user=admin_user)
        response = api_client.delete(f"/api/v1/patients/{patient.pk}/")
        assert response.status_code == status.HTTP_200_OK
        patient.refresh_from_db()
        assert patient.is_deleted is True
        assert patient.is_active is False

    def test_deactivate_patient(self, api_client, admin_user, patient):
        api_client.force_authenticate(user=admin_user)
        response = api_client.post(f"/api/v1/patients/{patient.pk}/deactivate/")
        assert response.status_code == status.HTTP_200_OK
        patient.refresh_from_db()
        assert patient.is_active is False

    def test_activate_patient(self, api_client, admin_user, patient):
        patient.is_active = False
        patient.save(update_fields=["is_active"])
        api_client.force_authenticate(user=admin_user)
        response = api_client.post(f"/api/v1/patients/{patient.pk}/activate/")
        assert response.status_code == status.HTTP_200_OK
        patient.refresh_from_db()
        assert patient.is_active is True

    def test_search_patients(self, api_client, receptionist_user, patient):
        api_client.force_authenticate(user=receptionist_user)
        response = api_client.get("/api/v1/patients/", {"search": "Costa"})
        assert response.status_code == status.HTTP_200_OK
        assert response.data["data"]["count"] >= 1

    def test_check_duplicate(self, api_client, receptionist_user, patient):
        api_client.force_authenticate(user=receptionist_user)
        response = api_client.get(
            "/api/v1/patients/check-duplicate/",
            {
                "first_name": "Ana",
                "last_name": "Costa",
                "birth_date": "15/03/1990",
                "phone": "+245955111222",
            },
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["data"]["has_duplicates"] is True


@pytest.mark.django_db
class TestPatientRBAC:
    def test_doctor_cannot_create_patient(self, api_client, doctor_user):
        api_client.force_authenticate(user=doctor_user)
        response = api_client.post("/api/v1/patients/", PATIENT_PAYLOAD, format="json")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_doctor_can_list_patients(self, api_client, doctor_user, patient):
        api_client.force_authenticate(user=doctor_user)
        response = api_client.get("/api/v1/patients/")
        assert response.status_code == status.HTTP_200_OK

    def test_nurse_cannot_delete_patient(self, api_client, db, patient):
        nurse = User.objects.create_user(
            email="enf@test.gw",
            password="Enf@123",
            first_name="Enf",
            last_name="Teste",
            role=UserRole.ENFERMEIRO,
        )
        api_client.force_authenticate(user=nurse)
        response = api_client.delete(f"/api/v1/patients/{patient.pk}/")
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestNestedResources:
    def test_create_allergy(self, api_client, doctor_user, patient):
        api_client.force_authenticate(user=doctor_user)
        response = api_client.post(
            f"/api/v1/patients/{patient.pk}/allergies/",
            {
                "allergen": "Penicilina",
                "severity": "GRAVE",
                "reaction": "Urticária",
            },
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert PatientAllergy.objects.filter(patient=patient, allergen="Penicilina").exists()
        assert PatientHistory.objects.filter(event_type="ALERGIA").exists()

    def test_list_emergency_contacts(self, api_client, receptionist_user, patient):
        api_client.force_authenticate(user=receptionist_user)
        response = api_client.get(f"/api/v1/patients/{patient.pk}/emergency-contacts/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["data"]["count"] >= 1

    def test_patient_history(self, api_client, receptionist_user, patient):
        api_client.force_authenticate(user=receptionist_user)
        response = api_client.get(f"/api/v1/patients/{patient.pk}/history/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["data"]["count"] >= 1

    def test_audit_trail(self, api_client, admin_user, patient):
        api_client.force_authenticate(user=admin_user)
        response = api_client.get(f"/api/v1/patients/{patient.pk}/audit-trail/")
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestPatientServices:
    def test_patient_number_generation(self):
        from apps.patients.services.number_service import PatientNumberService

        number = PatientNumberService.generate_next()
        assert number.startswith("PAC-")
        assert number.endswith("00001") or "-0000" in number

    def test_minor_requires_emergency_contact(self, api_client, receptionist_user):
        api_client.force_authenticate(user=receptionist_user)
        payload = {
            "first_name": "Criança",
            "last_name": "Teste",
            "birth_date": "01/01/2020",
            "gender": "M",
            "phone": "+245955123456",
        }
        response = api_client.post("/api/v1/patients/", payload, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestIntegrationStubs:
    def test_appointments_endpoint(self, api_client, receptionist_user, patient):
        api_client.force_authenticate(user=receptionist_user)
        response = api_client.get(f"/api/v1/patients/{patient.pk}/appointments/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["data"]["module_ready"] is True

    def test_balance_stub(self, api_client, receptionist_user, patient):
        api_client.force_authenticate(user=receptionist_user)
        response = api_client.get(f"/api/v1/patients/{patient.pk}/balance/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["data"]["currency"] == "XOF"


@pytest.mark.django_db
class TestPatientAuditIntegration:
    def test_export_is_audited(self, api_client, admin_user):
        api_client.force_authenticate(user=admin_user)
        response = api_client.get("/api/v1/patients/export/", {"export_format": "csv"})
        assert response.status_code == status.HTTP_200_OK
        assert AuditLog.objects.filter(action=AuditAction.PATIENT_EXPORT).exists()

    def test_print_is_audited(self, api_client, admin_user, patient):
        api_client.force_authenticate(user=admin_user)
        response = api_client.get(f"/api/v1/patients/{patient.pk}/print/")
        assert response.status_code == status.HTTP_200_OK
        assert AuditLog.objects.filter(
            action=AuditAction.PATIENT_PRINT,
            resource_id=str(patient.pk),
        ).exists()
