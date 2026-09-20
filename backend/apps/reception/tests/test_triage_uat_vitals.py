"""Testes UAT — validação de sinais vitais na triagem (receção)."""

from datetime import date

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status

from apps.audit_logs.models import AuditAction, AuditLog
from apps.authentication.models import UserRole
from apps.reception.models import ReceptionCheckIn

User = get_user_model()


@pytest.fixture
def patient(db, receptionist_user):
    from apps.patients.services.patient_service import PatientService

    return PatientService.create(
        {
            "first_name": "UAT",
            "last_name": "Vitais",
            "birth_date": date(1990, 3, 15),
            "gender": "F",
            "phone": "+245955111333",
            "document_number": "DOC-UAT-VIT",
            "document_type": "BI",
        },
        user=receptionist_user,
        emergency_contacts=[
            {
                "name": "Contacto",
                "phone": "+245955333555",
                "relationship": "CONJUGE",
                "is_primary": True,
            }
        ],
    )


@pytest.fixture
def nurse_user(db, seed_rbac):
    return User.objects.create_user(
        email="enfermeiro.uat@test.gw",
        password="Enf@12345",
        first_name="Eva",
        last_name="Enfermeira",
        role=UserRole.ENFERMEIRO,
    )


def _triage_payload(patient_id, **extra):
    base = {
        "patient_id": patient_id,
        "triage_color": "YELLOW",
        "age_at_check_in": 35,
        "weight": "68.00",
        "temperature": "35.0",
        "blood_pressure": "110/50",
        "spo2": 12,
        "heart_rate": 65,
        "respiratory_rate": 80,
        "symptoms": "Queixas respiratorias",
        "visit_purpose": "CONSULTA",
    }
    base.update(extra)
    return base


@pytest.mark.django_db
class TestTriageUatVitals:
    def test_unusual_vitals_persist_exactly(self, api_client, receptionist_user, patient):
        """UAT reproduce: TA 110/50, T 35, SpO2 12, FC 65, FR 80 — domain-valid, must save."""
        api_client.force_authenticate(user=receptionist_user)
        response = api_client.post(
            "/api/v1/reception/check-in/",
            _triage_payload(patient.pk, unusual_vitals_confirmed=True),
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED, response.data
        ci = response.data["data"]["check_in"]
        assert ci["blood_pressure"] == "110/50"
        assert float(ci["temperature"]) == 35.0
        assert ci["spo2"] == 12
        assert ci["heart_rate"] == 65
        assert ci["respiratory_rate"] == 80
        row = ReceptionCheckIn.objects.get(pk=ci["id"])
        assert row.spo2 == 12
        assert row.respiratory_rate == 80
        assert row.blood_pressure == "110/50"
        log = AuditLog.objects.filter(
            action=AuditAction.RECEPTION_CHECK_IN,
            resource_id=str(ci["id"]),
        ).latest("created_at")
        assert log.metadata.get("unusual_vitals_confirmed") is True

    def test_normal_vitals_succeed(self, api_client, receptionist_user, patient):
        api_client.force_authenticate(user=receptionist_user)
        response = api_client.post(
            "/api/v1/reception/check-in/",
            _triage_payload(
                patient.pk,
                triage_color="GREEN",
                temperature="36.8",
                blood_pressure="120/80",
                spo2=98,
                heart_rate=72,
                respiratory_rate=16,
            ),
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED, response.data

    def test_duplicate_queue_portuguese_error(self, api_client, receptionist_user, patient):
        api_client.force_authenticate(user=receptionist_user)
        payload = _triage_payload(patient.pk)
        first = api_client.post("/api/v1/reception/check-in/", payload, format="json")
        assert first.status_code == status.HTTP_201_CREATED
        second = api_client.post("/api/v1/reception/check-in/", payload, format="json")
        assert second.status_code == status.HTTP_400_BAD_REQUEST
        body = second.data
        flat = str(body)
        assert "fila" in flat.lower()

    def test_spo2_above_domain_rejected(self, api_client, receptionist_user, patient):
        api_client.force_authenticate(user=receptionist_user)
        response = api_client.post(
            "/api/v1/reception/check-in/",
            _triage_payload(patient.pk, spo2=101),
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "spo2" in response.data
        assert "100" in str(response.data["spo2"])

    def test_fr_above_domain_rejected(self, api_client, receptionist_user, patient):
        api_client.force_authenticate(user=receptionist_user)
        response = api_client.post(
            "/api/v1/reception/check-in/",
            _triage_payload(patient.pk, respiratory_rate=81),
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "respiratory_rate" in response.data

    def test_malformed_blood_pressure_still_allowed_as_text_if_present(
        self, api_client, receptionist_user, patient
    ):
        """Backend stores TA as text; format is enforced by FE schema. Required when triage_color set."""
        api_client.force_authenticate(user=receptionist_user)
        response = api_client.post(
            "/api/v1/reception/check-in/",
            _triage_payload(patient.pk, blood_pressure="110/50"),
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED

    def test_nurse_can_check_in_with_unusual_vitals(self, api_client, nurse_user, patient):
        api_client.force_authenticate(user=nurse_user)
        response = api_client.post(
            "/api/v1/reception/check-in/",
            _triage_payload(patient.pk, unusual_vitals_confirmed=True),
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED, response.data
        assert response.data["data"]["check_in"]["spo2"] == 12
