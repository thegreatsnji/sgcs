"""Testes do módulo de receção."""

import pytest
from datetime import timedelta
from django.contrib.auth import get_user_model
from rest_framework import status

from apps.audit_logs.models import AuditAction, AuditLog
from apps.authentication.models import UserRole
from apps.reception.constants import CheckInStatus, QueuePriority, QueueStatus
from apps.reception.models import ReceptionCheckIn, WaitingQueue
from apps.reception.services.reception_service import ReceptionService

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


def _check_in(api_client, user, patient_id, **payload):
    api_client.force_authenticate(user=user)
    return api_client.post(
        "/api/v1/reception/check-in/",
        {"patient_id": patient_id, **payload},
        format="json",
    )


@pytest.mark.django_db
class TestReceptionCheckIn:
    def test_receptionist_can_check_in(self, api_client, receptionist_user, patient):
        response = _check_in(api_client, receptionist_user, patient.pk)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["success"] is True
        assert response.data["data"]["check_in"]["patient"]["id"] == patient.pk
        assert response.data["data"]["queue_entry"]["position"] == 1
        assert WaitingQueue.objects.filter(patient=patient).count() == 1

    def test_doctor_cannot_check_in(self, api_client, doctor_user, patient):
        response = _check_in(api_client, doctor_user, patient.pk)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_duplicate_queue_rejected(self, api_client, receptionist_user, patient):
        _check_in(api_client, receptionist_user, patient.pk)
        response = _check_in(api_client, receptionist_user, patient.pk)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_check_in_creates_audit_log(self, api_client, receptionist_user, patient):
        _check_in(api_client, receptionist_user, patient.pk)
        assert AuditLog.objects.filter(action=AuditAction.RECEPTION_CHECK_IN).exists()

    def test_triage_red_is_immediate(self, api_client, receptionist_user, patient):
        response = _check_in(
            api_client,
            receptionist_user,
            patient.pk,
            triage_color="RED",
            age_at_check_in=45,
            weight="70.00",
            temperature="38.5",
            blood_pressure="140/90",
            symptoms="Dor torácica intensa",
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["data"]["check_in"]["priority"] == QueuePriority.EMERGENCY
        assert response.data["data"]["check_in"]["triage_color"] == "RED"
        assert response.data["data"]["queue_entry"]["estimated_wait_minutes"] == 0

    def test_triage_green_wait_time(self, api_client, receptionist_user, patient):
        response = _check_in(
            api_client,
            receptionist_user,
            patient.pk,
            triage_color="GREEN",
            age_at_check_in=30,
            weight="65.00",
            temperature="36.8",
            blood_pressure="120/80",
            symptoms="Febre ligeira",
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["data"]["check_in"]["priority"] == QueuePriority.NORMAL
        assert response.data["data"]["queue_entry"]["estimated_wait_minutes"] == 120

    def test_emergency_goes_to_top(self, api_client, receptionist_user, patient):
        from apps.patients.services.patient_service import PatientService

        patient2 = PatientService.create(
            {
                "first_name": "Bruno",
                "last_name": "Silva",
                "birth_date": __import__("datetime").date(1985, 1, 10),
                "gender": "M",
                "phone": "+245955222333",
                "document_number": "DOC002",
                "document_type": "BI",
            },
            user=receptionist_user,
            emergency_contacts=[
                {
                    "name": "Contacto",
                    "phone": "+245955444555",
                    "relationship": "CONJUGE",
                    "is_primary": True,
                }
            ],
        )

        _check_in(api_client, receptionist_user, patient.pk)
        response = _check_in(
            api_client,
            receptionist_user,
            patient2.pk,
            priority=QueuePriority.EMERGENCY,
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["data"]["queue_entry"]["position"] == 1

        first = WaitingQueue.objects.get(patient=patient2)
        second = WaitingQueue.objects.get(patient=patient)
        assert first.position == 1
        assert second.position == 2


@pytest.mark.django_db
class TestWaitingQueue:
    def test_list_queue(self, api_client, receptionist_user, patient):
        _check_in(api_client, receptionist_user, patient.pk)
        api_client.force_authenticate(user=receptionist_user)
        response = api_client.get("/api/v1/reception/queue/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["data"]["count"] == 1

    def test_update_queue_status(self, api_client, receptionist_user, patient):
        _check_in(api_client, receptionist_user, patient.pk)
        entry = WaitingQueue.objects.get(patient=patient)
        api_client.force_authenticate(user=receptionist_user)
        response = api_client.patch(
            f"/api/v1/reception/queue/{entry.pk}/",
            {"status": QueueStatus.COMPLETED},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        entry.refresh_from_db()
        assert entry.status == QueueStatus.COMPLETED
        assert AuditLog.objects.filter(action=AuditAction.RECEPTION_STATUS_CHANGE).exists()

    def test_assign_to_doctor(self, api_client, receptionist_user, doctor_user, patient):
        _check_in(api_client, receptionist_user, patient.pk)
        entry = WaitingQueue.objects.get(patient=patient)
        api_client.force_authenticate(user=receptionist_user)
        response = api_client.post(
            "/api/v1/reception/assign-to-doctor/",
            {"queue_id": entry.pk, "reason": "Consulta geral", "doctor_id": doctor_user.pk},
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED
        entry.refresh_from_db()
        assert entry.status == QueueStatus.IN_SERVICE
        check_in = ReceptionCheckIn.objects.get(pk=entry.check_in_id)
        assert check_in.status == CheckInStatus.IN_CONSULTATION
        assert AuditLog.objects.filter(action=AuditAction.RECEPTION_ASSIGN_DOCTOR).exists()


@pytest.mark.django_db
class TestReceptionHistory:
    def test_history_endpoint(self, api_client, receptionist_user, patient):
        _check_in(api_client, receptionist_user, patient.pk)
        api_client.force_authenticate(user=receptionist_user)
        response = api_client.get("/api/v1/reception/history/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["data"]["count"] >= 1


@pytest.mark.django_db
class TestReceptionDashboard:
    def test_reception_dashboard_kpis(self, api_client, receptionist_user, patient):
        ReceptionService.check_in(patient.pk, receptionist_user)
        api_client.force_authenticate(user=receptionist_user)
        response = api_client.get("/api/v1/dashboard/reception/")
        assert response.status_code == status.HTTP_200_OK
        cards = response.data["data"]["cards"]
        assert cards["patients_waiting"] == 1
        assert cards["average_wait_minutes"] < 60
        assert "average_wait_minutes" in cards
        assert "active_emergencies" in cards

    def test_reception_dashboard_ignores_stale_queue_for_avg_wait(
        self, api_client, receptionist_user, patient, db
    ):
        from django.utils import timezone

        ReceptionService.check_in(patient.pk, receptionist_user)
        stale = WaitingQueue.objects.select_related("check_in").first()
        stale.check_in.check_in_time = timezone.now() - timedelta(days=12)
        stale.check_in.save(update_fields=["check_in_time"])
        stale.status = QueueStatus.CALLED
        stale.save(update_fields=["status", "updated_at"])

        api_client.force_authenticate(user=receptionist_user)
        cards = api_client.get("/api/v1/dashboard/reception/").data["data"]["cards"]
        assert cards["average_wait_minutes"] < 120

    def test_doctor_cannot_view_reception_dashboard(self, api_client, doctor_user):
        """Médicos não têm reception.view — dashboard de receção é exclusivo da receção/admin."""
        api_client.force_authenticate(user=doctor_user)
        response = api_client.get("/api/v1/dashboard/reception/")
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestReceptionReferral:
    def test_create_referral(self, api_client, receptionist_user, patient):
        api_client.force_authenticate(user=receptionist_user)
        response = api_client.post(
            "/api/v1/reception/referrals/",
            {
                "patient_id": patient.pk,
                "to_department": "LAB",
                "reason": "Análises de rotina",
            },
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert AuditLog.objects.filter(action=AuditAction.RECEPTION_REFERRAL).exists()
