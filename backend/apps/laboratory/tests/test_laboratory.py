"""Testes do módulo de laboratório — Sprint 7 Fase 1."""

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status

from apps.appointments.services.clinical_record_service import ClinicalRecordService
from apps.audit_logs.models import AuditAction, AuditLog
from apps.authentication.models import UserRole
from apps.laboratory.constants import PedidoLaboratorialEstado
from apps.laboratory.models import PedidoLaboratorial
from apps.laboratory.services.laboratory_service import LaboratoryService
from apps.reception.models import WaitingQueue
from apps.reception.services.reception_service import ReceptionService

User = get_user_model()


@pytest.fixture
def lab_user(db):
    return User.objects.create_user(
        email="lab@test.gw",
        password="Lab@12345",
        first_name="Técnico",
        last_name="Laboratório",
        role=UserRole.LABORATORIO,
    )


@pytest.fixture
def doctor_user(db):
    return User.objects.create_user(
        email="medico.lab@test.gw",
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
            "first_name": "Lab",
            "last_name": "Paciente",
            "birth_date": __import__("datetime").date(1992, 1, 20),
            "gender": "F",
            "phone": "+245955000111",
            "document_number": "LABP001",
            "document_type": "BI",
        },
        user=receptionist_user,
    )


def _criar_pedido_via_consulta(receptionist_user, doctor_user, patient):
    check_in = ReceptionService.check_in(patient.pk, receptionist_user)
    entry = WaitingQueue.objects.get(check_in=check_in)
    ReceptionService.assign_to_doctor(queue_id=entry.pk, user=receptionist_user)
    from apps.appointments.models import Appointment
    from apps.appointments.services.appointment_service import AppointmentService

    appointment = Appointment.objects.get(patient=patient)
    AppointmentService.iniciar_consulta(appointment.pk, doctor_user)
    pedido_consulta = ClinicalRecordService.adicionar_pedido_laboratorio(
        appointment.pk,
        doctor_user,
        {"tipo_exame": "Hemograma completo", "prioridade": "NORMAL"},
    )
    return PedidoLaboratorial.objects.get(pedido_consulta=pedido_consulta)


@pytest.mark.django_db
class TestLaboratorioModelo:
    def test_numero_pedido_gerado(self, receptionist_user, doctor_user, patient):
        pedido = _criar_pedido_via_consulta(receptionist_user, doctor_user, patient)
        assert pedido.numero_pedido.startswith("LAB-")
        assert pedido.exames.count() == 1
        assert pedido.estado == PedidoLaboratorialEstado.PENDENTE


@pytest.mark.django_db
class TestLaboratorioServico:
    def test_fluxo_completo(self, lab_user, receptionist_user, doctor_user, patient):
        pedido = _criar_pedido_via_consulta(receptionist_user, doctor_user, patient)

        LaboratoryService.receber_pedido(pedido.pk, lab_user)
        pedido.refresh_from_db()
        assert pedido.estado == PedidoLaboratorialEstado.RECEBIDO

        LaboratoryService.registar_colheita(pedido.pk, lab_user)
        pedido.refresh_from_db()
        assert pedido.data_colheita is not None

        LaboratoryService.iniciar_processamento(pedido.pk, lab_user)
        pedido.refresh_from_db()
        assert pedido.estado == PedidoLaboratorialEstado.EM_PROCESSAMENTO

        LaboratoryService.concluir_exame(pedido.pk, lab_user)
        pedido.refresh_from_db()
        assert pedido.estado == PedidoLaboratorialEstado.CONCLUIDO
        assert pedido.pedido_consulta.estado == "CONCLUIDO"

    def test_nao_altera_concluido(self, lab_user, receptionist_user, doctor_user, patient):
        pedido = _criar_pedido_via_consulta(receptionist_user, doctor_user, patient)
        LaboratoryService.receber_pedido(pedido.pk, lab_user)
        LaboratoryService.iniciar_processamento(pedido.pk, lab_user)
        LaboratoryService.concluir_exame(pedido.pk, lab_user)
        with pytest.raises(ValueError, match="concluído"):
            LaboratoryService.actualizar_pedido(pedido.pk, lab_user, observacoes="x")


@pytest.mark.django_db
class TestLaboratorioAPI:
    def test_listar_pendentes(self, api_client, lab_user, receptionist_user, doctor_user, patient, seed_rbac):
        _criar_pedido_via_consulta(receptionist_user, doctor_user, patient)
        api_client.force_authenticate(user=lab_user)
        response = api_client.get("/api/v1/laboratory/pending/")
        assert response.status_code == 200
        assert response.data["data"]["count"] >= 1

    def test_receber_pedido(self, api_client, lab_user, receptionist_user, doctor_user, patient, seed_rbac):
        pedido = _criar_pedido_via_consulta(receptionist_user, doctor_user, patient)
        api_client.force_authenticate(user=lab_user)
        response = api_client.post(f"/api/v1/laboratory/{pedido.pk}/receive/")
        assert response.status_code == 200
        assert AuditLog.objects.filter(action=AuditAction.PEDIDO_LABORATORIO_RECEBIDO).exists()

    def test_workflow_api(self, api_client, lab_user, receptionist_user, doctor_user, patient, seed_rbac):
        pedido = _criar_pedido_via_consulta(receptionist_user, doctor_user, patient)
        api_client.force_authenticate(user=lab_user)
        api_client.post(f"/api/v1/laboratory/{pedido.pk}/receive/")
        api_client.post(f"/api/v1/laboratory/{pedido.pk}/collect/")
        api_client.post(f"/api/v1/laboratory/{pedido.pk}/start/")
        response = api_client.post(f"/api/v1/laboratory/{pedido.pk}/finish/")
        assert response.status_code == 200
        assert response.data["data"]["estado"] == "CONCLUIDO"


@pytest.mark.django_db
class TestLaboratorioRBAC:
    def test_medico_sem_permissao_receive(
        self, api_client, doctor_user, receptionist_user, patient, seed_rbac
    ):
        pedido = _criar_pedido_via_consulta(receptionist_user, doctor_user, patient)
        api_client.force_authenticate(user=doctor_user)
        response = api_client.post(f"/api/v1/laboratory/{pedido.pk}/receive/")
        assert response.status_code == 403


@pytest.mark.django_db
class TestLaboratorioDashboard:
    def test_dashboard(self, api_client, lab_user, receptionist_user, doctor_user, patient, seed_rbac):
        _criar_pedido_via_consulta(receptionist_user, doctor_user, patient)
        api_client.force_authenticate(user=lab_user)
        response = api_client.get("/api/v1/dashboard/laboratory/")
        assert response.status_code == 200
        assert "indicadores" in response.data["data"]
