"""Sprint 23.5 — Atribuição explícita de médico pela Receção."""

from datetime import date, timedelta
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status

from apps.appointments.constants import AppointmentStatus
from apps.appointments.models import Appointment
from apps.appointments.services.appointment_service import AppointmentService
from apps.audit_logs.models import AuditAction, AuditLog
from apps.authentication.models import UserRole
from apps.billing.constants import CATALOGO_VERSAO_ATIVA, FaturaEstado
from apps.billing.models import Servico
from apps.billing.services.billing_service import BillingService
from apps.patients.services.patient_service import PatientService
from apps.reception.constants import QueueStatus
from apps.reception.models import WaitingQueue
from apps.reception.services.reception_service import ReceptionService

User = get_user_model()


@pytest.fixture
def doctor_a(db):
    return User.objects.create_user(
        email="dr.a@test.gw",
        password="Medico@123",
        first_name="João",
        last_name="Silva",
        role=UserRole.MEDICO,
    )


@pytest.fixture
def doctor_b(db):
    return User.objects.create_user(
        email="dr.b@test.gw",
        password="Medico@123",
        first_name="Maria",
        last_name="Gomes",
        role=UserRole.MEDICO,
    )


@pytest.fixture
def nurse_user(db):
    return User.objects.create_user(
        email="enf.assign@test.gw",
        password="Enf@123",
        first_name="Ana",
        last_name="Enfermeira",
        role=UserRole.ENFERMEIRO,
    )


@pytest.fixture
def patient(db, receptionist_user):
    return PatientService.create(
        {
            "first_name": "Utente",
            "last_name": "Assign",
            "birth_date": date(1990, 1, 10),
            "gender": "F",
            "phone": "+245955700100",
            "document_number": "ASSIGN-001",
            "document_type": "BI",
        },
        user=receptionist_user,
        emergency_contacts=[
            {
                "name": "Contacto",
                "phone": "+245955700101",
                "relationship": "CONJUGE",
                "is_primary": True,
            }
        ],
    )


@pytest.fixture
def servico(db):
    return Servico.objects.create(
        codigo="ASSIGN-10K",
        nome="Consulta assign",
        categoria="CONSULTA",
        preco=Decimal("10000"),
        preco_confirmado=True,
        versao_catalogo=CATALOGO_VERSAO_ATIVA,
    )


def _queue_entry(receptionist_user, patient):
    check_in = ReceptionService.check_in(patient.pk, receptionist_user)
    return WaitingQueue.objects.get(check_in=check_in)


@pytest.mark.django_db
class TestDoctorAssignmentOptions:
    def test_lista_apenas_medicos_activos(
        self, api_client, receptionist_user, doctor_a, doctor_b, nurse_user, patient
    ):
        api_client.force_authenticate(user=receptionist_user)
        response = api_client.get(
            "/api/v1/reception/doctor-assignment-options/",
            {"patient_id": patient.pk},
        )
        assert response.status_code == 200
        ids = {row["id"] for row in response.data["data"]["doctors"]}
        assert doctor_a.pk in ids
        assert doctor_b.pk in ids
        assert nurse_user.pk not in ids
        assert receptionist_user.pk not in ids
        assert all("full_name" in row for row in response.data["data"]["doctors"])
        assert all("availability_label" in row for row in response.data["data"]["doctors"])


@pytest.mark.django_db
class TestExplicitAssign:
    def test_assign_requires_doctor_id(self, receptionist_user, patient, doctor_a):
        entry = _queue_entry(receptionist_user, patient)
        with pytest.raises(ValueError, match="Seleccione um médico"):
            ReceptionService.assign_to_doctor(queue_id=entry.pk, user=receptionist_user)

    def test_assign_to_doctor_a_and_doctor_queues(
        self, api_client, receptionist_user, doctor_a, doctor_b, patient
    ):
        entry = _queue_entry(receptionist_user, patient)
        ReceptionService.assign_to_doctor(
            queue_id=entry.pk, user=receptionist_user, doctor_id=doctor_a.pk
        )
        appointment = Appointment.objects.get(patient=patient)
        assert appointment.doctor_id == doctor_a.pk
        assert appointment.status == AppointmentStatus.EM_ESPERA
        entry.refresh_from_db()
        assert entry.status == QueueStatus.IN_SERVICE

        api_client.force_authenticate(user=doctor_a)
        qa = api_client.get("/api/v1/appointments/queue/")
        assert qa.status_code == 200
        ids_a = {row["id"] for row in qa.data["data"]["results"]}
        assert appointment.pk in ids_a

        api_client.force_authenticate(user=doctor_b)
        qb = api_client.get("/api/v1/appointments/queue/")
        ids_b = {row["id"] for row in qb.data["data"]["results"]}
        assert appointment.pk not in ids_b

    def test_unavailable_keeps_waiting_and_payment(
        self, receptionist_user, doctor_a, patient, servico
    ):
        entry = _queue_entry(receptionist_user, patient)
        fatura = BillingService.gerar_fatura(
            receptionist_user,
            paciente_id=patient.pk,
            itens=[{"servico_id": servico.pk, "quantidade": 1}],
        )
        p = BillingService.registar_pagamento(
            fatura.pk, receptionist_user, valor=Decimal("10000"), metodo_pagamento="DINHEIRO"
        )
        BillingService.confirmar_pagamento(p.pk, receptionist_user)

        other = PatientService.create(
            {
                "first_name": "Outro",
                "last_name": "Paciente",
                "birth_date": date(1985, 2, 2),
                "gender": "M",
                "phone": "+245955700200",
                "document_number": "ASSIGN-002",
                "document_type": "BI",
            },
            user=receptionist_user,
            emergency_contacts=[
                {
                    "name": "C",
                    "phone": "+245955700201",
                    "relationship": "CONJUGE",
                    "is_primary": True,
                }
            ],
        )
        busy = AppointmentService.criar_consulta(
            patient_id=other.pk,
            user=receptionist_user,
            doctor_id=doctor_a.pk,
        )
        busy.status = AppointmentStatus.EM_CONSULTA
        busy.consultation_date = timezone.localdate()
        busy.save(update_fields=["status", "consultation_date"])

        with pytest.raises(ValueError, match="não está disponível"):
            ReceptionService.assign_to_doctor(
                queue_id=entry.pk, user=receptionist_user, doctor_id=doctor_a.pk
            )

        entry.refresh_from_db()
        fatura.refresh_from_db()
        assert entry.status == QueueStatus.WAITING
        assert fatura.estado == FaturaEstado.PAGA
        assert Appointment.objects.filter(patient=patient).count() == 0

    def test_no_duplicates_on_assign(self, receptionist_user, doctor_a, patient):
        entry = _queue_entry(receptionist_user, patient)
        ReceptionService.assign_to_doctor(
            queue_id=entry.pk, user=receptionist_user, doctor_id=doctor_a.pk
        )
        assert WaitingQueue.objects.filter(patient=patient).count() == 1
        assert Appointment.objects.filter(patient=patient).count() == 1


@pytest.mark.django_db
class TestReassignmentAndSchedule:
    def test_reassign_before_start(self, receptionist_user, doctor_a, doctor_b, patient):
        entry = _queue_entry(receptionist_user, patient)
        ReceptionService.assign_to_doctor(
            queue_id=entry.pk, user=receptionist_user, doctor_id=doctor_a.pk
        )
        ReceptionService.assign_to_doctor(
            queue_id=entry.pk, user=receptionist_user, doctor_id=doctor_b.pk
        )
        appointment = Appointment.objects.get(patient=patient)
        assert appointment.doctor_id == doctor_b.pk
        assert Appointment.objects.filter(patient=patient).count() == 1
        assert AuditLog.objects.filter(action=AuditAction.RECEPTION_ASSIGN_DOCTOR).count() >= 2

    def test_reassign_blocked_after_start(
        self, api_client, receptionist_user, doctor_a, doctor_b, patient
    ):
        entry = _queue_entry(receptionist_user, patient)
        ReceptionService.assign_to_doctor(
            queue_id=entry.pk, user=receptionist_user, doctor_id=doctor_a.pk
        )
        appointment = Appointment.objects.get(patient=patient)
        api_client.force_authenticate(user=doctor_a)
        assert api_client.post(f"/api/v1/appointments/{appointment.pk}/start/").status_code == 200
        with pytest.raises(ValueError, match="já foi iniciada"):
            ReceptionService.assign_to_doctor(
                queue_id=entry.pk, user=receptionist_user, doctor_id=doctor_b.pk
            )
        appointment.refresh_from_db()
        assert appointment.doctor_id == doctor_a.pk

    def test_marcacao_preserves_doctor(self, receptionist_user, doctor_a, patient):
        when = timezone.now() + timedelta(hours=2)
        appointment = AppointmentService.criar_consulta(
            patient_id=patient.pk,
            user=receptionist_user,
            doctor_id=doctor_a.pk,
            scheduled_at=when,
        )
        appointment = AppointmentService.confirmar_chegada(appointment.pk, receptionist_user)
        assert appointment.check_in_id
        opts = ReceptionService.get_doctor_assignment_options(
            patient.pk, check_in_id=appointment.check_in_id
        )
        assert opts["scheduled_doctor"] is not None
        assert opts["scheduled_doctor"]["id"] == doctor_a.pk

        entry = WaitingQueue.objects.get(check_in_id=appointment.check_in_id)
        ReceptionService.assign_to_doctor(
            queue_id=entry.pk, user=receptionist_user, doctor_id=doctor_a.pk
        )
        appointment.refresh_from_db()
        assert appointment.doctor_id == doctor_a.pk
        assert Appointment.objects.filter(patient=patient).count() == 1

    def test_queue_shows_assigned_doctor(
        self, api_client, receptionist_user, doctor_a, patient
    ):
        entry = _queue_entry(receptionist_user, patient)
        ReceptionService.assign_to_doctor(
            queue_id=entry.pk, user=receptionist_user, doctor_id=doctor_a.pk
        )
        api_client.force_authenticate(user=receptionist_user)
        response = api_client.get("/api/v1/reception/queue/")
        assert response.status_code == 200
        row = next(r for r in response.data["data"]["results"] if r["id"] == entry.pk)
        assert row["assigned_doctor"]["id"] == doctor_a.pk
        assert "Silva" in row["assigned_doctor"]["full_name"]

    def test_queue_filter_by_doctor(
        self, api_client, receptionist_user, doctor_a, doctor_b, patient
    ):
        entry = _queue_entry(receptionist_user, patient)
        ReceptionService.assign_to_doctor(
            queue_id=entry.pk, user=receptionist_user, doctor_id=doctor_a.pk
        )
        api_client.force_authenticate(user=receptionist_user)
        filtered = api_client.get("/api/v1/reception/queue/", {"doctor": doctor_a.pk})
        assert any(r["id"] == entry.pk for r in filtered.data["data"]["results"])
        other = api_client.get("/api/v1/reception/queue/", {"doctor": doctor_b.pk})
        assert all(r["id"] != entry.pk for r in other.data["data"]["results"])


@pytest.mark.django_db
class TestReceptionClinicalStillBlocked:
    def test_cannot_start_or_write_clinical(
        self, api_client, receptionist_user, doctor_a, patient
    ):
        entry = _queue_entry(receptionist_user, patient)
        ReceptionService.assign_to_doctor(
            queue_id=entry.pk, user=receptionist_user, doctor_id=doctor_a.pk
        )
        appointment = Appointment.objects.get(patient=patient)
        api_client.force_authenticate(user=receptionist_user)
        assert api_client.post(f"/api/v1/appointments/{appointment.pk}/start/").status_code == 403
        assert (
            api_client.get(f"/api/v1/appointments/{appointment.pk}/clinical/").status_code
            == 403
        )
        assert (
            api_client.post(
                f"/api/v1/patients/{patient.pk}/allergies/",
                {"allergen": "X", "severity": "LEVE"},
                format="json",
            ).status_code
            == 403
        )
