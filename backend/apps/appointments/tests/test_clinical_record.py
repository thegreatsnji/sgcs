"""Testes do Prontuário Clínico Eletrónico — Sprint 6 Fase 2."""

import pytest
from django.utils import timezone
from rest_framework import status

from apps.appointments.constants import AppointmentStatus
from apps.appointments.models import (
    AnotacaoClinica,
    Appointment,
    Diagnostico,
    PedidoImagiologia,
    PedidoLaboratorio,
    Seguimento,
    SinaisVitais,
)
from apps.appointments.services.appointment_service import AppointmentService
from apps.appointments.services.clinical_record_service import ClinicalRecordService
from apps.audit_logs.models import AuditAction, AuditLog
from apps.authentication.models import UserRole
from apps.reception.models import WaitingQueue
from apps.reception.services.reception_service import ReceptionService

User = __import__("django.contrib.auth", fromlist=["get_user_model"]).get_user_model()


@pytest.fixture
def doctor_user(db):
    return User.objects.create_user(
        email="medico.pce@test.gw",
        password="Medico@123",
        first_name="Paulo",
        last_name="Médico",
        role=UserRole.MEDICO,
    )


@pytest.fixture
def nurse_user(db):
    return User.objects.create_user(
        email="enfermeiro.pce@test.gw",
        password="Enfermeiro@123",
        first_name="Maria",
        last_name="Enfermeira",
        role=UserRole.ENFERMEIRO,
    )


@pytest.fixture
def patient(db, receptionist_user):
    from apps.patients.services.patient_service import PatientService

    return PatientService.create(
        {
            "first_name": "Carlos",
            "last_name": "PCE",
            "birth_date": __import__("datetime").date(1985, 6, 10),
            "gender": "M",
            "phone": "+245955777888",
            "document_number": "PCE001",
            "document_type": "BI",
            "blood_type": "O+",
        },
        user=receptionist_user,
    )


def _start_consultation(receptionist_user, doctor_user, patient):
    check_in = ReceptionService.check_in(patient.pk, receptionist_user)
    entry = WaitingQueue.objects.get(check_in=check_in)
    ReceptionService.assign_to_doctor(queue_id=entry.pk, user=receptionist_user)
    appointment = Appointment.objects.get(patient=patient)
    AppointmentService.iniciar_consulta(appointment.pk, doctor_user)
    appointment.refresh_from_db()
    return appointment


@pytest.mark.django_db
class TestPCEModelos:
    def test_imc_calculado_automaticamente(self, receptionist_user, doctor_user, patient):
        appointment = _start_consultation(receptionist_user, doctor_user, patient)
        sinais = SinaisVitais.objects.create(
            consulta=appointment,
            peso=80,
            altura=180,
            registado_por=doctor_user,
        )
        assert sinais.imc == pytest.approx(24.69, rel=0.01)

    def test_diagnostico_principal(self, receptionist_user, doctor_user, patient):
        appointment = _start_consultation(receptionist_user, doctor_user, patient)
        diag = Diagnostico.objects.create(
            consulta=appointment,
            codigo_cid10="J06.9",
            descricao="Infecção respiratória",
            tipo="PRINCIPAL",
            registado_por=doctor_user,
        )
        assert diag.tipo == "PRINCIPAL"


@pytest.mark.django_db
class TestPCEServico:
    def test_bloqueia_edicao_fora_de_consulta(self, receptionist_user, doctor_user, patient):
        appointment = AppointmentService.criar_consulta(patient_id=patient.pk, user=receptionist_user)
        with pytest.raises(ValueError, match="em curso"):
            ClinicalRecordService.guardar_sinais_vitais(
                appointment.pk,
                doctor_user,
                {"peso": 70, "altura": 175},
            )

    def test_apenas_medico_preenche(self, receptionist_user, doctor_user, nurse_user, patient):
        appointment = _start_consultation(receptionist_user, doctor_user, patient)
        with pytest.raises(ValueError, match="Apenas médicos"):
            ClinicalRecordService.guardar_sinais_vitais(
                appointment.pk,
                nurse_user,
                {"peso": 70},
            )

    def test_guardar_soap_e_sinais(self, receptionist_user, doctor_user, patient):
        appointment = _start_consultation(receptionist_user, doctor_user, patient)
        ClinicalRecordService.guardar_sinais_vitais(
            appointment.pk,
            doctor_user,
            {"peso": 75, "altura": 178, "frequencia_cardiaca": 72},
        )
        ClinicalRecordService.guardar_soap(
            appointment.pk,
            doctor_user,
            {"subjetivo": "Dor de cabeça", "plano": "Analgésico"},
        )
        prontuario = ClinicalRecordService.obter_prontuario(appointment.pk)
        assert prontuario["sinais_vitais"]["imc"] is not None
        assert prontuario["anotacao_soap"]["subjetivo"] == "Dor de cabeça"


@pytest.mark.django_db
class TestPCEAPI:
    def _auth_doctor(self, api_client, doctor_user):
        api_client.force_authenticate(user=doctor_user)

    def test_get_prontuario(self, api_client, receptionist_user, doctor_user, patient):
        appointment = _start_consultation(receptionist_user, doctor_user, patient)
        self._auth_doctor(api_client, doctor_user)
        response = api_client.get(f"/api/v1/appointments/{appointment.pk}/clinical/")
        assert response.status_code == 200
        data = response.data["data"]
        assert "paciente" in data
        assert data["paciente"]["blood_type"] == "O+"
        assert data["consulta"]["editavel"] is True

    def test_post_sinais_vitais(self, api_client, receptionist_user, doctor_user, patient):
        appointment = _start_consultation(receptionist_user, doctor_user, patient)
        self._auth_doctor(api_client, doctor_user)
        response = api_client.post(
            f"/api/v1/appointments/{appointment.pk}/vital-signs/",
            {"peso": 82, "altura": 175, "temperatura": "36.8"},
            format="json",
        )
        assert response.status_code == 201
        assert response.data["data"]["sinais_vitais"]["imc"] is not None
        assert AuditLog.objects.filter(action=AuditAction.SINAIS_VITAIS_REGISTADOS).exists()

    def test_post_diagnostico(self, api_client, receptionist_user, doctor_user, patient):
        appointment = _start_consultation(receptionist_user, doctor_user, patient)
        self._auth_doctor(api_client, doctor_user)
        response = api_client.post(
            f"/api/v1/appointments/{appointment.pk}/diagnoses/",
            {"codigo_cid10": "R51", "descricao": "Cefaleia", "tipo": "PRINCIPAL"},
            format="json",
        )
        assert response.status_code == 201
        assert AuditLog.objects.filter(action=AuditAction.DIAGNOSTICO_ADICIONADO).exists()

    def test_post_laboratorio(self, api_client, receptionist_user, doctor_user, patient):
        appointment = _start_consultation(receptionist_user, doctor_user, patient)
        self._auth_doctor(api_client, doctor_user)
        response = api_client.post(
            f"/api/v1/appointments/{appointment.pk}/laboratory/",
            {"tipo_exame": "Hemograma completo"},
            format="json",
        )
        assert response.status_code == 201
        assert PedidoLaboratorio.objects.filter(consulta=appointment).exists()

    def test_post_imagiologia(self, api_client, receptionist_user, doctor_user, patient):
        appointment = _start_consultation(receptionist_user, doctor_user, patient)
        self._auth_doctor(api_client, doctor_user)
        response = api_client.post(
            f"/api/v1/appointments/{appointment.pk}/imaging/",
            {"tipo_exame": "Raio-X tórax"},
            format="json",
        )
        assert response.status_code == 201
        assert PedidoImagiologia.objects.filter(consulta=appointment).exists()

    def test_post_seguimento(self, api_client, receptionist_user, doctor_user, patient):
        appointment = _start_consultation(receptionist_user, doctor_user, patient)
        self._auth_doctor(api_client, doctor_user)
        retorno = (timezone.localdate() + timezone.timedelta(days=30)).isoformat()
        response = api_client.post(
            f"/api/v1/appointments/{appointment.pk}/follow-up/",
            {"data_retorno": retorno, "motivo": "Reavaliação"},
            format="json",
        )
        assert response.status_code == 201
        assert Seguimento.objects.filter(consulta=appointment).exists()

    def test_patch_clinical_legado(self, api_client, receptionist_user, doctor_user, patient):
        appointment = _start_consultation(receptionist_user, doctor_user, patient)
        self._auth_doctor(api_client, doctor_user)
        response = api_client.patch(
            f"/api/v1/appointments/{appointment.pk}/clinical/",
            {"chief_complaint": "Febre", "clinical_notes": "Há 3 dias"},
            format="json",
        )
        assert response.status_code == 200
        assert AuditLog.objects.filter(action=AuditAction.CONSULTA_CLINICA_EDITADA).exists()

    def test_bloqueia_apos_conclusao(self, api_client, receptionist_user, doctor_user, patient):
        appointment = _start_consultation(receptionist_user, doctor_user, patient)
        AppointmentService.concluir_consulta(appointment.pk, doctor_user)
        self._auth_doctor(api_client, doctor_user)
        response = api_client.post(
            f"/api/v1/appointments/{appointment.pk}/vital-signs/",
            {"peso": 70},
            format="json",
        )
        assert response.status_code == 400


@pytest.mark.django_db
class TestPCERBAC:
    def test_enfermeiro_sem_permissao_diagnostico(
        self, api_client, receptionist_user, doctor_user, nurse_user, patient, seed_rbac
    ):
        appointment = _start_consultation(receptionist_user, doctor_user, patient)
        api_client.force_authenticate(user=nurse_user)
        response = api_client.post(
            f"/api/v1/appointments/{appointment.pk}/diagnoses/",
            {"codigo_cid10": "R51", "descricao": "Teste"},
            format="json",
        )
        assert response.status_code == 403


@pytest.mark.django_db
class TestPCEWorkflow:
    def test_fluxo_completo_pce(self, api_client, receptionist_user, doctor_user, patient):
        appointment = _start_consultation(receptionist_user, doctor_user, patient)
        api_client.force_authenticate(user=doctor_user)

        api_client.post(
            f"/api/v1/appointments/{appointment.pk}/vital-signs/",
            {"peso": 70, "altura": 170},
            format="json",
        )
        api_client.post(
            f"/api/v1/appointments/{appointment.pk}/diagnoses/",
            {"codigo_cid10": "J00", "descricao": "Nasofaringite", "tipo": "PRINCIPAL"},
            format="json",
        )
        api_client.post(
            f"/api/v1/appointments/{appointment.pk}/laboratory/",
            {"tipo_exame": "PCR"},
            format="json",
        )

        finish = api_client.post(f"/api/v1/appointments/{appointment.pk}/finish/", format="json")
        assert finish.status_code == 200
        appointment.refresh_from_db()
        assert appointment.status == AppointmentStatus.CONCLUIDA

        blocked = api_client.patch(
            f"/api/v1/appointments/{appointment.pk}/clinical/",
            {"notes": "tentativa"},
            format="json",
        )
        assert blocked.status_code == 400
