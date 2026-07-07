"""Testes do módulo de consultas — Sprint 6 Fase 1."""

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status

from apps.appointments.constants import AppointmentStatus
from apps.appointments.models import Appointment
from apps.appointments.services.appointment_service import AppointmentService
from apps.audit_logs.models import AuditAction, AuditLog
from apps.authentication.models import UserRole
from apps.reception.constants import CheckInStatus, QueueStatus
from apps.reception.models import WaitingQueue
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
def doctor_user_b(db):
    return User.objects.create_user(
        email="medico2@test.gw",
        password="Medico@123",
        first_name="Ana",
        last_name="Médica",
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


def _handoff(receptionist_user, patient):
    check_in = ReceptionService.check_in(patient.pk, receptionist_user)
    entry = WaitingQueue.objects.get(check_in=check_in)
    return ReceptionService.assign_to_doctor(queue_id=entry.pk, user=receptionist_user)


@pytest.mark.django_db
class TestConsultaModelo:
    def test_numero_consulta_gerado(self, receptionist_user, patient):
        appointment = AppointmentService.criar_consulta(patient_id=patient.pk, user=receptionist_user)
        assert appointment.appointment_number.startswith("CON-")
        assert appointment.consultation_date is not None


@pytest.mark.django_db
class TestConsultaFluxo:
    def test_handoff_cria_consulta_em_espera(self, receptionist_user, patient):
        _handoff(receptionist_user, patient)
        appointment = Appointment.objects.get(patient=patient)
        assert appointment.status == AppointmentStatus.EM_ESPERA
        assert appointment.queue_entry is not None

    def test_fluxo_completo(self, api_client, receptionist_user, doctor_user, patient):
        _handoff(receptionist_user, patient)
        appointment = Appointment.objects.get(patient=patient)

        api_client.force_authenticate(user=doctor_user)
        assert api_client.post(f"/api/v1/appointments/{appointment.pk}/start/").status_code == 200
        appointment.refresh_from_db()
        assert appointment.status == AppointmentStatus.EM_CONSULTA

        complete = api_client.post(
            f"/api/v1/appointments/{appointment.pk}/finish/",
            {"diagnosis": "Gripe", "clinical_notes": "Repouso"},
            format="json",
        )
        assert complete.status_code == 200
        appointment.refresh_from_db()
        assert appointment.status == AppointmentStatus.CONCLUIDA
        assert appointment.duration_minutes >= 0
        assert AuditLog.objects.filter(action=AuditAction.CONSULTA_CONCLUIDA).exists()


@pytest.mark.django_db
class TestConsultaRBAC:
    def test_rececionista_confirma(self, api_client, receptionist_user, patient):
        appointment = AppointmentService.criar_consulta(patient_id=patient.pk, user=receptionist_user)
        api_client.force_authenticate(user=receptionist_user)
        response = api_client.post(f"/api/v1/appointments/{appointment.pk}/confirm/")
        assert response.status_code == 200

    def test_medico_nao_cancela_sem_permissao_rececionista(self, api_client, doctor_user, receptionist_user, patient):
        appointment = AppointmentService.criar_consulta(patient_id=patient.pk, user=receptionist_user)
        api_client.force_authenticate(user=doctor_user)
        response = api_client.post(
            f"/api/v1/appointments/{appointment.pk}/cancel/",
            {"reason": "teste"},
            format="json",
        )
        assert response.status_code == 403


@pytest.mark.django_db
class TestConsultaAPI:
    def test_listar_hoje(self, api_client, receptionist_user, patient):
        AppointmentService.criar_consulta(patient_id=patient.pk, user=receptionist_user)
        api_client.force_authenticate(user=receptionist_user)
        response = api_client.get("/api/v1/appointments/today/")
        assert response.status_code == 200
        assert response.data["data"]["count"] >= 1

    def test_calendario(self, api_client, receptionist_user, patient):
        AppointmentService.criar_consulta(patient_id=patient.pk, user=receptionist_user)
        today = timezone.localdate()
        api_client.force_authenticate(user=receptionist_user)
        response = api_client.get(
            f"/api/v1/appointments/calendar/?start={today}&end={today}"
        )
        assert response.status_code == 200

    def test_sobreposicao_medico(self, receptionist_user, doctor_user, patient):
        when = timezone.now() + timezone.timedelta(hours=2)
        AppointmentService.criar_consulta(
            patient_id=patient.pk,
            user=receptionist_user,
            doctor_id=doctor_user.pk,
            scheduled_at=when,
        )
        with pytest.raises(ValueError, match="já tem consulta"):
            AppointmentService.criar_consulta(
                patient_id=patient.pk,
                user=receptionist_user,
                doctor_id=doctor_user.pk,
                scheduled_at=when + timezone.timedelta(minutes=15),
            )

    def test_dashboard_consultas(self, api_client, doctor_user, receptionist_user, patient):
        AppointmentService.criar_consulta(patient_id=patient.pk, user=receptionist_user)
        api_client.force_authenticate(user=doctor_user)
        response = api_client.get("/api/v1/dashboard/consultas/")
        assert response.status_code == 200
        assert "indicadores" in response.data["data"]

    def test_endpoint_legado_complete(self, api_client, doctor_user, receptionist_user, patient):
        _handoff(receptionist_user, patient)
        appointment = Appointment.objects.get(patient=patient)
        api_client.force_authenticate(user=doctor_user)
        api_client.post(f"/api/v1/appointments/{appointment.pk}/start/")
        response = api_client.post(f"/api/v1/appointments/{appointment.pk}/complete/", format="json")
        assert response.status_code == 200
