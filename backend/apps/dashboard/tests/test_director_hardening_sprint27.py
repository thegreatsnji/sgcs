"""Sprint 27 — Hardening do perfil DIRECTOR (supervisão)."""

from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status

from apps.appointments.constants import PedidoLaboratorioEstadoFaturacao
from apps.appointments.models import PedidoLaboratorio
from apps.authentication.models import UserRole
from apps.billing.constants import MetodoPagamento
from apps.billing.models import Servico
from apps.billing.services.billing_service import BillingService
from apps.dashboard.director_dashboard_service import DirectorDashboardService
from apps.laboratory.constants import PedidoLaboratorialEstado, ResultadoLaboratorialEstado
from apps.laboratory.models import PedidoLaboratorial, ResultadoLaboratorial
from apps.patients.constants import HistoryEventType
from apps.patients.models import PatientHistory
from apps.patients.services.history_service import PatientHistoryService
from apps.pharmacy.models import MedicamentoUrgencia
from apps.users.services.rbac_service import RBACService

User = get_user_model()


@pytest.fixture
def director_user(db, seed_rbac):
    return User.objects.create_user(
        email="director.s27@test.gw",
        password="Dir@12345",
        first_name="Director",
        last_name="Sprint27",
        role=UserRole.DIRECTOR,
        is_active=True,
    )


@pytest.fixture
def doctor_user(db, seed_rbac):
    return User.objects.create_user(
        email="medico.s27@test.gw",
        password="Medico@123",
        first_name="Med",
        last_name="Sprint27",
        role=UserRole.MEDICO,
        is_active=True,
    )


@pytest.fixture
def patient(db, receptionist_user):
    from apps.patients.services.patient_service import PatientService

    return PatientService.create(
        {
            "first_name": "Dir",
            "last_name": "Utente",
            "birth_date": date(1991, 5, 5),
            "gender": "F",
            "phone": "+245955270001",
            "document_number": "DIR27001",
            "document_type": "BI",
        },
        user=receptionist_user,
    )


@pytest.fixture
def servico_10k(db):
    return Servico.objects.create(
        codigo="DIR-10K",
        nome="Consulta Director Test",
        categoria="CONSULTA",
        preco=Decimal("10000.00"),
        preco_confirmado=True,
    )


def _emitir(user, patient, servico, *, qty=1):
    return BillingService.gerar_fatura(
        user,
        paciente_id=patient.pk,
        itens=[{"servico_id": servico.pk, "quantidade": qty}],
    )


def _pagar(user, fatura, valor):
    pag = BillingService.registar_pagamento(
        fatura.pk,
        user,
        valor=Decimal(valor),
        metodo_pagamento=MetodoPagamento.DINHEIRO,
    )
    return BillingService.confirmar_pagamento(pag.pk, user)


@pytest.mark.django_db
class TestDirectorDashboardAccess:
    def test_dashboard_sem_reception_view(self, api_client, director_user):
        perms = RBACService.get_user_permissions(director_user)
        assert "reception.view" not in perms
        assert "reception.edit" not in perms
        assert "dashboard.view" in perms

        api_client.force_authenticate(user=director_user)
        blocked = api_client.get("/api/v1/dashboard/reception/")
        assert blocked.status_code == status.HTTP_403_FORBIDDEN

        ok = api_client.get("/api/v1/dashboard/director/", {"periodo": "hoje"})
        assert ok.status_code == status.HTTP_200_OK
        body = ok.data["data"]
        assert "financeiro" in body
        assert "operacional" in body
        assert body["financeiro"]["ok"] is True
        assert "total_faturado" in body["financeiro"]["data"]
        assert "saldo_pendente" in body["financeiro"]["data"]

    def test_periodo_personalizado_exige_datas(self, api_client, director_user):
        api_client.force_authenticate(user=director_user)
        r = api_client.get("/api/v1/dashboard/director/", {"periodo": "personalizado"})
        assert r.status_code == status.HTTP_400_BAD_REQUEST

    def test_periodo_personalizado_ok(self, api_client, director_user):
        api_client.force_authenticate(user=director_user)
        hoje = timezone.localdate()
        r = api_client.get(
            "/api/v1/dashboard/director/",
            {
                "periodo": "personalizado",
                "data_inicio": (hoje - timedelta(days=2)).isoformat(),
                "data_fim": hoje.isoformat(),
            },
        )
        assert r.status_code == status.HTTP_200_OK
        assert r.data["data"]["periodo"]["modo"] == "personalizado"


@pytest.mark.django_db
class TestDirectorFinanceiro:
    def test_resumo_faturado_recebido_saldo_reducoes(
        self, api_client, director_user, receptionist_user, patient, servico_10k
    ):
        fatura = _emitir(receptionist_user, patient, servico_10k)
        _pagar(receptionist_user, fatura, "7000")

        api_client.force_authenticate(user=director_user)
        r = api_client.get("/api/v1/dashboard/director/", {"periodo": "hoje"})
        assert r.status_code == status.HTTP_200_OK
        fin = r.data["data"]["financeiro"]["data"]
        assert Decimal(fin["total_faturado"]) == Decimal("10000.00")
        assert Decimal(fin["total_recebido"]) == Decimal("7000.00")
        assert Decimal(fin["saldo_pendente"]) == Decimal("3000.00")
        assert fin["faturas_com_saldo"] == 1
        assert Decimal(fin["saldo_pendente"]) != Decimal(fin["faturas_com_saldo"])

    def test_pagamento_parcial(
        self, api_client, director_user, receptionist_user, patient, servico_10k
    ):
        fatura = _emitir(receptionist_user, patient, servico_10k)
        _pagar(receptionist_user, fatura, "6000")
        fatura.refresh_from_db()
        assert fatura.estado == "PARCIAL"

        api_client.force_authenticate(user=director_user)
        fin = api_client.get("/api/v1/dashboard/director/", {"periodo": "hoje"}).data["data"][
            "financeiro"
        ]["data"]
        assert Decimal(fin["total_faturado"]) == Decimal("10000.00")
        assert Decimal(fin["total_recebido"]) == Decimal("6000.00")
        assert Decimal(fin["saldo_pendente"]) == Decimal("4000.00")

    def test_historico_migrado_isolado(
        self, api_client, director_user, receptionist_user, patient, servico_10k
    ):
        PatientHistoryService.record(
            patient,
            event_type=HistoryEventType.REGISTO,
            title="Pagamento histórico Excel",
            description="Não deve entrar na receita",
            event_date=timezone.now(),
            source_module="MIGRACAO_EXCEL_SAUVIDA",
            metadata={
                "source": "MIGRACAO_EXCEL_SAUVIDA",
                "valor_liquido_original": "999999",
            },
            user=receptionist_user,
        )
        assert PatientHistory.objects.filter(
            patient=patient, source_module="MIGRACAO_EXCEL_SAUVIDA"
        ).exists()

        api_client.force_authenticate(user=director_user)
        fin = api_client.get("/api/v1/dashboard/director/", {"periodo": "hoje"}).data["data"][
            "financeiro"
        ]["data"]
        assert Decimal(fin["total_faturado"]) == Decimal("0.00")
        assert Decimal(fin["total_recebido"]) == Decimal("0.00")
        assert Decimal(fin["saldo_pendente"]) == Decimal("0.00")
        assert Decimal(fin["total_reducoes"]) == Decimal("0.00")

    def test_error_isolation_financeiro(self):
        with patch(
            "apps.dashboard.director_dashboard_service.get_resumo_operacional",
            side_effect=RuntimeError("boom"),
        ):
            data = DirectorDashboardService.get_summary(
                data_inicio=timezone.localdate(),
                data_fim=timezone.localdate(),
            )
        assert data["financeiro"]["ok"] is False
        assert "Não foi possível" in data["financeiro"]["error"]
        assert data["operacional"]["ok"] is True
        assert data["stock"]["ok"] is True


@pytest.mark.django_db
class TestDirectorOperacionalLabStock:
    def test_utentes_e_consultas_agregados(
        self, api_client, director_user, receptionist_user, doctor_user, patient
    ):
        from apps.appointments.services.appointment_service import AppointmentService
        from apps.reception.constants import QueueStatus
        from apps.reception.services.reception_service import ReceptionService

        check_in = ReceptionService.check_in(patient.pk, receptionist_user)
        ReceptionService.update_queue_entry(
            check_in.queue_entry.pk,
            receptionist_user,
            status=QueueStatus.COMPLETED,
        )
        AppointmentService.criar_consulta(
            patient_id=patient.pk,
            user=receptionist_user,
            doctor_id=doctor_user.pk,
            scheduled_at=timezone.now(),
        )

        api_client.force_authenticate(user=director_user)
        op = api_client.get("/api/v1/dashboard/director/", {"periodo": "hoje"}).data["data"][
            "operacional"
        ]["data"]
        assert op["utentes_atendidos"] >= 1
        assert op["utentes_atendidos_definicao"] == "check_ins_concluidos"
        assert op["consultas"] >= 1

    def test_lab_agregado(self, api_client, director_user, patient, doctor_user, receptionist_user):
        from apps.appointments.services.appointment_service import AppointmentService
        from apps.laboratory.services.laboratory_service import LaboratoryService
        from apps.laboratory.services.number_service import LaboratoryNumberService

        appt = AppointmentService.criar_consulta(
            patient_id=patient.pk,
            user=receptionist_user,
            doctor_id=doctor_user.pk,
            scheduled_at=timezone.now(),
        )
        for i in range(2):
            pc = PedidoLaboratorio.objects.create(
                consulta=appt,
                tipo_exame=f"Glicemia-{i}",
                estado_faturacao=PedidoLaboratorioEstadoFaturacao.AGUARDA_REGULARIZACAO,
                solicitado_por=doctor_user,
            )
            LaboratoryService.criar_de_pedido_consulta(pc, user=doctor_user)

        for i in range(3):
            pedido = PedidoLaboratorial.objects.create(
                numero_pedido=LaboratoryNumberService.generate(),
                consulta=appt,
                paciente=patient,
                medico=doctor_user,
                estado=PedidoLaboratorialEstado.CONCLUIDO,
                prioridade="NORMAL",
            )
            ResultadoLaboratorial.objects.create(
                pedido_laboratorial=pedido,
                estado=ResultadoLaboratorialEstado.RESULTADO_PENDENTE,
            )

        api_client.force_authenticate(user=director_user)
        lab = api_client.get("/api/v1/dashboard/director/", {"periodo": "hoje"}).data["data"][
            "laboratorio"
        ]["data"]
        assert lab["aguardam_regularizacao"] == 2
        assert lab["aguardam_validacao"] == 3
        assert "parametros" not in lab
        assert "conclusao" not in lab

    def test_stock_agregado(self, api_client, director_user):
        hoje = date.today()
        MedicamentoUrgencia.objects.create(
            codigo="DIR-BAIXO",
            nome="Baixo",
            quantidade_stock=2,
            stock_minimo=5,
            validade=hoje + timedelta(days=90),
            activo=True,
        )
        MedicamentoUrgencia.objects.create(
            codigo="DIR-SEM",
            nome="Sem",
            quantidade_stock=0,
            stock_minimo=1,
            validade=hoje + timedelta(days=90),
            activo=True,
        )
        MedicamentoUrgencia.objects.create(
            codigo="DIR-PROX",
            nome="Prox",
            quantidade_stock=10,
            stock_minimo=1,
            validade=hoje + timedelta(days=5),
            activo=True,
        )
        MedicamentoUrgencia.objects.create(
            codigo="DIR-EXP",
            nome="Exp",
            quantidade_stock=3,
            stock_minimo=1,
            validade=hoje - timedelta(days=1),
            activo=True,
        )

        api_client.force_authenticate(user=director_user)
        stock = api_client.get("/api/v1/dashboard/director/", {"periodo": "hoje"}).data["data"][
            "stock"
        ]["data"]
        assert stock["stock_baixo"] == 1
        assert stock["sem_stock"] == 1
        assert stock["proximos_validade"] == 1
        assert stock["expirados"] == 1


@pytest.mark.django_db
class TestDirectorRBAC:
    def test_seed_sem_writes_operacionais(self, director_user):
        perms = RBACService.get_user_permissions(director_user)
        fordenied = [
            "billing.create",
            "billing.payment",
            "billing.edit",
            "reception.view",
            "reception.create",
            "reception.edit",
            "appointments.clinical",
            "appointments.diagnosis",
            "appointments.start",
            "doctors.prescription",
            "laboratory.results.view",
            "laboratory.results.validate",
            "stock.entry",
            "stock.exit",
            "stock.adjust",
            "patients.edit",
            "patients.create",
            "finance.cash",
            "finance.expense",
            "users.view",
            "settings.system",
        ]
        for p in fordenied:
            assert p not in perms, p
        for allowed in [
            "dashboard.view",
            "billing.view",
            "reports.view",
            "stock.view",
            "patients.view",
        ]:
            assert allowed in perms, allowed

    def test_billing_write_403(
        self, api_client, director_user, receptionist_user, patient, servico_10k
    ):
        fatura = _emitir(receptionist_user, patient, servico_10k)
        api_client.force_authenticate(user=director_user)
        pay = api_client.post(
            "/api/v1/billing/payments/",
            {
                "fatura": fatura.pk,
                "metodo_pagamento": "DINHEIRO",
                "valor": "1000",
            },
            format="json",
        )
        assert pay.status_code == status.HTTP_403_FORBIDDEN
        cancel = api_client.post(f"/api/v1/billing/invoices/{fatura.pk}/cancel/")
        assert cancel.status_code == status.HTTP_403_FORBIDDEN
        create = api_client.post(
            "/api/v1/billing/invoices/",
            {
                "paciente": patient.pk,
                "itens": [{"servico": servico_10k.pk, "quantidade": 1}],
            },
            format="json",
        )
        assert create.status_code == status.HTTP_403_FORBIDDEN

    def test_clinical_prescription_lab_stock_403(
        self, api_client, director_user, receptionist_user, doctor_user, patient
    ):
        from apps.appointments.services.appointment_service import AppointmentService

        appt = AppointmentService.criar_consulta(
            patient_id=patient.pk,
            user=receptionist_user,
            doctor_id=doctor_user.pk,
            scheduled_at=timezone.now(),
        )
        api_client.force_authenticate(user=director_user)

        soap = api_client.patch(
            f"/api/v1/appointments/{appt.pk}/clinical/",
            {"subjetivo": "não deve"},
            format="json",
        )
        assert soap.status_code == status.HTTP_403_FORBIDDEN

        presc = api_client.post(
            "/api/v1/prescriptions/",
            {
                "consulta": appt.pk,
                "medicamentos": [
                    {
                        "nome": "Paracetamol",
                        "dose": "500mg",
                        "frequencia": "8/8h",
                        "duracao": "3 dias",
                    }
                ],
            },
            format="json",
        )
        assert presc.status_code == status.HTTP_403_FORBIDDEN

        lab_validate = api_client.post("/api/v1/laboratory/results/1/validate/")
        assert lab_validate.status_code in (
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND,
        )

        med = MedicamentoUrgencia.objects.create(
            codigo="DIR-SAIDA",
            nome="DirStock",
            quantidade_stock=5,
            stock_minimo=1,
            validade=date.today() + timedelta(days=60),
            activo=True,
        )
        saida = api_client.post(
            f"/api/v1/stock/items/{med.pk}/saida/",
            {"quantidade": 1, "motivo": "teste"},
            format="json",
        )
        assert saida.status_code == status.HTTP_403_FORBIDDEN

        patient_edit = api_client.patch(
            f"/api/v1/patients/{patient.pk}/",
            {"phone": "+245955999888"},
            format="json",
        )
        assert patient_edit.status_code == status.HTTP_403_FORBIDDEN

    def test_metricas_permitidas_200(self, api_client, director_user):
        api_client.force_authenticate(user=director_user)
        assert (
            api_client.get("/api/v1/dashboard/director/", {"periodo": "hoje"}).status_code
            == status.HTTP_200_OK
        )
        assert (
            api_client.get("/api/v1/billing/resumo-operacional/", {"periodo": "hoje"}).status_code
            == status.HTTP_200_OK
        )
        assert api_client.get("/api/v1/billing/invoices/").status_code == status.HTTP_200_OK
        assert api_client.get("/api/v1/stock/dashboard/").status_code == status.HTTP_200_OK
        assert api_client.get("/api/v1/dashboard/executive/").status_code == status.HTTP_200_OK
