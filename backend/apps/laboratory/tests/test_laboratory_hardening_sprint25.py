"""Testes Sprint 25 — hardening do fluxo laboratorial."""

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status

from apps.appointments.services.clinical_record_service import ClinicalRecordService
from apps.authentication.models import UserRole
from apps.laboratory.billing import MSG_AGUARDA_REGULARIZACAO
from apps.laboratory.constants import PedidoLaboratorialEstado
from apps.laboratory.models import PedidoLaboratorial, ResultadoLaboratorial
from apps.laboratory.services.laboratory_result_service import LaboratoryResultService
from apps.laboratory.services.laboratory_service import LaboratoryService
from apps.reception.constants import QueuePriority
from apps.reception.models import WaitingQueue
from apps.reception.services.reception_service import ReceptionService

User = get_user_model()


@pytest.fixture
def lab_user(db):
    return User.objects.create_user(
        email="lab.s25@test.gw",
        password="Lab@12345",
        first_name="Técnico",
        last_name="Sprint25",
        role=UserRole.LABORATORIO,
    )


@pytest.fixture
def doctor_user(db):
    return User.objects.create_user(
        email="medico.s25@test.gw",
        password="Medico@123",
        first_name="Maria",
        last_name="Médica",
        role=UserRole.MEDICO,
    )


@pytest.fixture
def patient(db, receptionist_user):
    from apps.patients.services.patient_service import PatientService

    return PatientService.create(
        {
            "first_name": "LabHard",
            "last_name": "Paciente",
            "birth_date": __import__("datetime").date(1988, 3, 15),
            "gender": "F",
            "phone": "+245955000333",
            "document_number": "LABS25001",
            "document_type": "BI",
        },
        user=receptionist_user,
    )


def _criar_pedido(receptionist_user, doctor_user, patient, *, tipo="Hemograma", prioridade="NORMAL"):
    check_in = ReceptionService.check_in(patient.pk, receptionist_user)
    entry = WaitingQueue.objects.get(check_in=check_in)
    ReceptionService.assign_to_doctor(
        queue_id=entry.pk, user=receptionist_user, doctor_id=doctor_user.pk
    )
    from apps.appointments.models import Appointment
    from apps.appointments.services.appointment_service import AppointmentService

    appointment = Appointment.objects.get(patient=patient)
    AppointmentService.iniciar_consulta(appointment.pk, doctor_user)
    pedido_consulta = ClinicalRecordService.adicionar_pedido_laboratorio(
        appointment.pk,
        doctor_user,
        {"tipo_exame": tipo, "prioridade": prioridade},
    )
    pedido = PedidoLaboratorial.objects.get(pedido_consulta=pedido_consulta)
    return pedido, appointment, pedido_consulta


def _regularizar(pedido_consulta):
    pedido_consulta.estado_faturacao = "REGULARIZADO"
    pedido_consulta.save(update_fields=["estado_faturacao", "updated_at"])


@pytest.mark.django_db
class TestRegularizacaoGate:
    def test_start_bloqueado_sem_regularizacao(
        self, lab_user, receptionist_user, doctor_user, patient
    ):
        pedido, _, _ = _criar_pedido(receptionist_user, doctor_user, patient)
        LaboratoryService.receber_pedido(pedido.pk, lab_user)
        with pytest.raises(ValueError, match="regularização"):
            LaboratoryService.iniciar_processamento(pedido.pk, lab_user)

    def test_start_ok_apos_regularizacao(
        self, lab_user, receptionist_user, doctor_user, patient
    ):
        pedido, _, pedido_consulta = _criar_pedido(receptionist_user, doctor_user, patient)
        LaboratoryService.receber_pedido(pedido.pk, lab_user)
        _regularizar(pedido_consulta)
        LaboratoryService.iniciar_processamento(pedido.pk, lab_user)
        pedido.refresh_from_db()
        assert pedido.estado == PedidoLaboratorialEstado.EM_PROCESSAMENTO

    def test_api_start_bloqueado(
        self, api_client, lab_user, receptionist_user, doctor_user, patient, seed_rbac
    ):
        pedido, _, _ = _criar_pedido(receptionist_user, doctor_user, patient)
        api_client.force_authenticate(user=lab_user)
        api_client.post(f"/api/v1/laboratory/{pedido.pk}/receive/")
        response = api_client.post(f"/api/v1/laboratory/{pedido.pk}/start/")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert MSG_AGUARDA_REGULARIZACAO in str(response.data)

    def test_serializer_expoe_estado_faturacao_minimo(
        self, api_client, lab_user, receptionist_user, doctor_user, patient, seed_rbac
    ):
        pedido, _, _ = _criar_pedido(receptionist_user, doctor_user, patient)
        api_client.force_authenticate(user=lab_user)
        response = api_client.get(f"/api/v1/laboratory/{pedido.pk}/")
        assert response.status_code == 200
        data = response.data["data"]
        assert data["estado_faturacao"] == "AGUARDA_REGULARIZACAO"
        assert data["estado_faturacao_label"] == "Aguarda regularização"
        assert data["pode_processar"] is False
        assert "preco" not in data
        assert "montante" not in data


@pytest.mark.django_db
class TestPrioridadeOrdenacao:
    def test_emergencia_antes_de_normal(
        self, lab_user, receptionist_user, doctor_user, patient
    ):
        pedido_normal, appointment, pc_n = _criar_pedido(
            receptionist_user, doctor_user, patient, tipo="Glicemia", prioridade="NORMAL"
        )
        pc_u = ClinicalRecordService.adicionar_pedido_laboratorio(
            appointment.pk,
            doctor_user,
            {"tipo_exame": "Troponina", "prioridade": QueuePriority.EMERGENCY},
        )
        pedido_urg = PedidoLaboratorial.objects.get(pedido_consulta=pc_u)
        _regularizar(pc_n)
        _regularizar(pc_u)
        ids = list(LaboratoryService.listar_pendentes().values_list("id", flat=True))
        assert ids.index(pedido_urg.pk) < ids.index(pedido_normal.pk)


@pytest.mark.django_db
class TestPesquisaFiltros:
    def test_pesquisa_por_exame(
        self, api_client, lab_user, receptionist_user, doctor_user, patient, seed_rbac
    ):
        _criar_pedido(receptionist_user, doctor_user, patient, tipo="Hemograma completo")
        api_client.force_authenticate(user=lab_user)
        response = api_client.get("/api/v1/laboratory/pending/", {"q": "Hemograma"})
        assert response.status_code == 200
        assert response.data["data"]["count"] >= 1

    def test_filtro_estado_faturacao(
        self, api_client, lab_user, receptionist_user, doctor_user, patient, seed_rbac
    ):
        pedido, _, _ = _criar_pedido(receptionist_user, doctor_user, patient)
        api_client.force_authenticate(user=lab_user)
        response = api_client.get(
            "/api/v1/laboratory/",
            {"estado_faturacao": "AGUARDA_REGULARIZACAO"},
        )
        assert response.status_code == 200
        ids = [r["id"] for r in response.data["data"]["results"]]
        assert pedido.pk in ids


@pytest.mark.django_db
class TestIdentificacaoPaciente:
    def test_pedido_inclui_sexo_e_nascimento(
        self, api_client, lab_user, receptionist_user, doctor_user, patient, seed_rbac
    ):
        pedido, _, _ = _criar_pedido(receptionist_user, doctor_user, patient)
        api_client.force_authenticate(user=lab_user)
        response = api_client.get(f"/api/v1/laboratory/{pedido.pk}/")
        pac = response.data["data"]["paciente"]
        assert pac["gender"] == "F"
        assert pac["gender_label"] == "Feminino"
        assert pac["birth_date"] is not None
        assert pac["age_years"] is not None
        assert pac["patient_number"]


@pytest.mark.django_db
class TestConclusaoClinicaAposValidacao:
    def test_finish_nao_conclui_pedido_clinico(
        self, lab_user, receptionist_user, doctor_user, patient
    ):
        pedido, _, pedido_consulta = _criar_pedido(receptionist_user, doctor_user, patient)
        _regularizar(pedido_consulta)
        LaboratoryService.receber_pedido(pedido.pk, lab_user)
        LaboratoryService.iniciar_processamento(pedido.pk, lab_user)
        LaboratoryService.concluir_exame(pedido.pk, lab_user)
        pedido_consulta.refresh_from_db()
        assert pedido_consulta.estado == "PENDENTE"

    def test_validacao_conclui_pedido_clinico(
        self, lab_user, receptionist_user, doctor_user, patient
    ):
        pedido, _, pedido_consulta = _criar_pedido(receptionist_user, doctor_user, patient)
        _regularizar(pedido_consulta)
        LaboratoryService.receber_pedido(pedido.pk, lab_user)
        LaboratoryService.iniciar_processamento(pedido.pk, lab_user)
        resultado = LaboratoryResultService.criar_resultado(
            pedido.pk, lab_user, conclusao="POSITIVO"
        )
        LaboratoryResultService.validar_resultado(resultado.pk, lab_user)
        pedido_consulta.refresh_from_db()
        assert pedido_consulta.estado == "CONCLUIDO"


@pytest.mark.django_db
class TestRececaoBridge:
    def test_mark_idempotente(
        self, api_client, receptionist_user, doctor_user, patient, seed_rbac
    ):
        _, _, pedido_consulta = _criar_pedido(receptionist_user, doctor_user, patient)
        api_client.force_authenticate(user=receptionist_user)
        url = f"/api/v1/reception/mark-lab-order-billed/{pedido_consulta.pk}/"
        first = api_client.post(url)
        second = api_client.post(url)
        assert first.status_code == 200
        assert second.status_code == 200
        assert first.data["data"]["already_regularized"] is False
        assert second.data["data"]["already_regularized"] is True
        assert second.data["data"]["estado_faturacao"] == "REGULARIZADO"
        pedido_consulta.refresh_from_db()
        assert pedido_consulta.estado_faturacao == "REGULARIZADO"

    def test_rececao_lista_pendentes(
        self, api_client, receptionist_user, doctor_user, patient, seed_rbac
    ):
        _, _, pedido_consulta = _criar_pedido(receptionist_user, doctor_user, patient)
        api_client.force_authenticate(user=receptionist_user)
        response = api_client.get("/api/v1/reception/pending-clinical-lab-orders/")
        assert response.status_code == 200
        ids = [r["id"] for r in response.data["data"]]
        assert pedido_consulta.pk in ids

    def test_rececao_nao_ve_resultado_clinico(
        self, api_client, lab_user, receptionist_user, doctor_user, patient, seed_rbac
    ):
        pedido, _, pedido_consulta = _criar_pedido(receptionist_user, doctor_user, patient)
        _regularizar(pedido_consulta)
        LaboratoryService.receber_pedido(pedido.pk, lab_user)
        LaboratoryService.iniciar_processamento(pedido.pk, lab_user)
        resultado = LaboratoryResultService.criar_resultado(
            pedido.pk, lab_user, conclusao="Hb 13"
        )
        LaboratoryResultService.validar_resultado(resultado.pk, lab_user)
        api_client.force_authenticate(user=receptionist_user)
        response = api_client.get(f"/api/v1/laboratory/results/{resultado.pk}/")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_pedido_com_servico_catalogo(
        self, api_client, receptionist_user, doctor_user, patient, seed_rbac
    ):
        from decimal import Decimal

        from apps.billing.models import Servico

        servico = Servico.objects.create(
            codigo="LAB-HEMO",
            nome="Hemograma completo",
            categoria="LABORATORIO",
            preco=Decimal("5000"),
            activo=True,
            preco_confirmado=True,
        )
        check_in = ReceptionService.check_in(patient.pk, receptionist_user)
        entry = WaitingQueue.objects.get(check_in=check_in)
        ReceptionService.assign_to_doctor(
            queue_id=entry.pk, user=receptionist_user, doctor_id=doctor_user.pk
        )
        from apps.appointments.models import Appointment
        from apps.appointments.services.appointment_service import AppointmentService

        appointment = Appointment.objects.get(patient=patient)
        AppointmentService.iniciar_consulta(appointment.pk, doctor_user)
        api_client.force_authenticate(user=doctor_user)
        response = api_client.post(
            f"/api/v1/appointments/{appointment.pk}/laboratory/",
            {"servico_id": servico.pk, "prioridade": "NORMAL"},
            format="json",
        )
        assert response.status_code == 201
        pedido = response.data["data"]["pedidos_laboratorio"][-1]
        assert pedido["servico_id"] == servico.pk
        assert pedido["tipo_exame"] == "Hemograma completo"
        assert pedido["estado_faturacao"] == "AGUARDA_REGULARIZACAO"

        api_client.force_authenticate(user=receptionist_user)
        pending = api_client.get("/api/v1/reception/pending-clinical-lab-orders/")
        assert pending.status_code == 200
        row = next(r for r in pending.data["data"] if r["id"] == pedido["id"])
        assert row["servico"]["id"] == servico.pk
        assert row["servico"]["nome"] == "Hemograma completo"


@pytest.mark.django_db
class TestMultiplosETextual:
    def test_dois_pedidos_independentes(
        self, lab_user, receptionist_user, doctor_user, patient
    ):
        pedido_a, appointment, pc_a = _criar_pedido(
            receptionist_user, doctor_user, patient, tipo="Hemograma"
        )
        pc_b = ClinicalRecordService.adicionar_pedido_laboratorio(
            appointment.pk, doctor_user, {"tipo_exame": "Glicemia"}
        )
        pedido_b = PedidoLaboratorial.objects.get(pedido_consulta=pc_b)
        _regularizar(pc_a)
        _regularizar(pc_b)
        LaboratoryService.receber_pedido(pedido_a.pk, lab_user)
        LaboratoryService.iniciar_processamento(pedido_a.pk, lab_user)
        res_a = LaboratoryResultService.criar_resultado(
            pedido_a.pk, lab_user, conclusao="Normal"
        )
        LaboratoryResultService.validar_resultado(res_a.pk, lab_user)
        pedido_b.refresh_from_db()
        assert pedido_b.estado == PedidoLaboratorialEstado.PENDENTE
        assert not ResultadoLaboratorial.objects.filter(pedido_laboratorial=pedido_b).exists()

    def test_resultado_textual_sem_parametros(
        self, lab_user, receptionist_user, doctor_user, patient
    ):
        pedido, _, pc = _criar_pedido(
            receptionist_user, doctor_user, patient, tipo="Teste HCG"
        )
        _regularizar(pc)
        LaboratoryService.receber_pedido(pedido.pk, lab_user)
        LaboratoryService.iniciar_processamento(pedido.pk, lab_user)
        resultado = LaboratoryResultService.criar_resultado(
            pedido.pk, lab_user, conclusao="POSITIVO"
        )
        assert resultado.parametros.count() == 0
        assert resultado.conclusao == "POSITIVO"


@pytest.mark.django_db
class TestLabPrivacy:
    def test_lab_sem_billing_view(self, lab_user, seed_rbac):
        from apps.users.services.rbac_service import RBACService

        perms = RBACService.get_user_permissions(lab_user)
        assert "billing.view" not in perms
        assert "billing.edit" not in perms
        assert "appointments.clinical" not in perms
