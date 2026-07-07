"""Testes de resultados laboratoriais — Sprint 7 Fase 2."""

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status

from apps.appointments.services.clinical_record_service import ClinicalRecordService
from apps.audit_logs.models import AuditAction, AuditLog
from apps.authentication.models import UserRole
from apps.laboratory.constants import ResultadoLaboratorialEstado
from apps.laboratory.models import PedidoLaboratorial, ResultadoLaboratorial
from apps.laboratory.services.laboratory_result_service import LaboratoryResultService
from apps.laboratory.services.laboratory_service import LaboratoryService
from apps.reception.models import WaitingQueue
from apps.reception.services.reception_service import ReceptionService

User = get_user_model()


@pytest.fixture
def lab_user(db):
    return User.objects.create_user(
        email="lab.results@test.gw",
        password="Lab@12345",
        first_name="Técnico",
        last_name="Resultados",
        role=UserRole.LABORATORIO,
    )


@pytest.fixture
def doctor_user(db):
    return User.objects.create_user(
        email="medico.results@test.gw",
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
            "first_name": "Result",
            "last_name": "Paciente",
            "birth_date": __import__("datetime").date(1990, 5, 10),
            "gender": "M",
            "phone": "+245955000222",
            "document_number": "LABR001",
            "document_type": "BI",
        },
        user=receptionist_user,
    )


def _pedido_em_processamento(receptionist_user, doctor_user, patient, lab_user):
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
    pedido = PedidoLaboratorial.objects.get(pedido_consulta=pedido_consulta)
    LaboratoryService.receber_pedido(pedido.pk, lab_user)
    LaboratoryService.iniciar_processamento(pedido.pk, lab_user)
    return pedido, appointment


def _criar_resultado_com_parametros(pedido, lab_user):
    resultado = LaboratoryResultService.criar_resultado(pedido.pk, lab_user, conclusao="Normal")
    LaboratoryResultService.adicionar_parametro(
        resultado.pk,
        lab_user,
        {
            "nome": "Hemoglobina",
            "valor": "13.5",
            "unidade": "g/dL",
            "valor_minimo": "12.5",
            "valor_maximo": "16.5",
            "ordem": 0,
        },
    )
    return resultado


@pytest.mark.django_db
class TestResultadoModelo:
    def test_criar_resultado(self, lab_user, receptionist_user, doctor_user, patient):
        pedido, _ = _pedido_em_processamento(receptionist_user, doctor_user, patient, lab_user)
        resultado = _criar_resultado_com_parametros(pedido, lab_user)
        assert resultado.estado == ResultadoLaboratorialEstado.RESULTADO_PENDENTE
        assert resultado.parametros.count() == 1
        assert resultado.parametros.first().interpretacao == "NORMAL"


@pytest.mark.django_db
class TestResultadoServico:
    def test_nao_edita_validado(self, lab_user, receptionist_user, doctor_user, patient):
        pedido, _ = _pedido_em_processamento(receptionist_user, doctor_user, patient, lab_user)
        resultado = _criar_resultado_com_parametros(pedido, lab_user)
        LaboratoryResultService.validar_resultado(resultado.pk, lab_user)
        with pytest.raises(ValueError, match="validado"):
            LaboratoryResultService.editar_resultado(resultado.pk, lab_user, observacoes="x")

    def test_validar_integra_consulta(self, lab_user, receptionist_user, doctor_user, patient):
        pedido, appointment = _pedido_em_processamento(receptionist_user, doctor_user, patient, lab_user)
        resultado = LaboratoryResultService.criar_resultado(
            pedido.pk, lab_user, conclusao="Hemograma dentro dos limites."
        )
        LaboratoryResultService.validar_resultado(resultado.pk, lab_user)
        pedido.refresh_from_db()
        appointment.refresh_from_db()
        assert pedido.estado == "CONCLUIDO"
        assert "Hemograma" in appointment.clinical_notes
        assert AuditLog.objects.filter(action=AuditAction.RESULTADO_VALIDADO).exists()


@pytest.mark.django_db
class TestResultadoAPI:
    def test_fluxo_api(self, api_client, lab_user, receptionist_user, doctor_user, patient, seed_rbac):
        pedido, _ = _pedido_em_processamento(receptionist_user, doctor_user, patient, lab_user)
        api_client.force_authenticate(user=lab_user)

        create_resp = api_client.post(
            "/api/v1/laboratory/results/",
            {
                "pedido_laboratorial": pedido.pk,
                "conclusao": "Resultado normal.",
                "parametros": [
                    {
                        "nome": "Leucócitos",
                        "valor": "7800",
                        "unidade": "/mm³",
                        "valor_minimo": "4000",
                        "valor_maximo": "11000",
                    }
                ],
            },
            format="json",
        )
        assert create_resp.status_code == status.HTTP_201_CREATED
        resultado_id = create_resp.data["data"]["id"]

        validate_resp = api_client.post(f"/api/v1/laboratory/results/{resultado_id}/validate/")
        assert validate_resp.status_code == 200
        assert validate_resp.data["data"]["estado"] == "VALIDADO"

        publish_resp = api_client.post(f"/api/v1/laboratory/results/{resultado_id}/publish/")
        assert publish_resp.status_code == 200
        assert publish_resp.data["data"]["estado"] == "ENTREGUE"

        list_resp = api_client.get("/api/v1/laboratory/results/")
        assert list_resp.status_code == 200
        assert list_resp.data["data"]["count"] >= 1

    def test_medico_pode_ver(self, api_client, lab_user, doctor_user, receptionist_user, patient, seed_rbac):
        pedido, _ = _pedido_em_processamento(receptionist_user, doctor_user, patient, lab_user)
        resultado = _criar_resultado_com_parametros(pedido, lab_user)
        api_client.force_authenticate(user=doctor_user)
        response = api_client.get(f"/api/v1/laboratory/results/{resultado.pk}/")
        assert response.status_code == 200


@pytest.mark.django_db
class TestResultadoRBAC:
    def test_medico_nao_cria(self, api_client, doctor_user, receptionist_user, patient, lab_user, seed_rbac):
        pedido, _ = _pedido_em_processamento(receptionist_user, doctor_user, patient, lab_user)
        api_client.force_authenticate(user=doctor_user)
        response = api_client.post(
            "/api/v1/laboratory/results/",
            {"pedido_laboratorial": pedido.pk},
            format="json",
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestResultadoDashboard:
    def test_indicadores_resultados(self, lab_user, receptionist_user, doctor_user, patient):
        pedido, _ = _pedido_em_processamento(receptionist_user, doctor_user, patient, lab_user)
        resultado = _criar_resultado_com_parametros(pedido, lab_user)
        LaboratoryResultService.validar_resultado(resultado.pk, lab_user)
        summary = LaboratoryService.get_dashboard_summary()
        assert "resultados" in summary
        assert summary["resultados"]["resultados_validados"] >= 1


@pytest.mark.django_db
class TestResultadoPCE:
    def test_prontuario_inclui_resultados(
        self, lab_user, doctor_user, receptionist_user, patient
    ):
        pedido, appointment = _pedido_em_processamento(receptionist_user, doctor_user, patient, lab_user)
        resultado = _criar_resultado_com_parametros(pedido, lab_user)
        LaboratoryResultService.validar_resultado(resultado.pk, lab_user)
        prontuario = ClinicalRecordService.obter_prontuario(appointment.pk)
        assert len(prontuario["resultados_laboratoriais"]) == 1
        assert prontuario["resultados_laboratoriais"][0]["numero_pedido"] == pedido.numero_pedido
