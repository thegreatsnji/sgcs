"""Testes do módulo de faturação — Sprint 8 Fase 1."""

from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status

from apps.audit_logs.models import AuditAction, AuditLog
from apps.authentication.models import UserRole
from apps.billing.constants import FaturaEstado, OrcamentoEstado, PagamentoEstado
from apps.billing.models import Fatura, Recibo, Servico
from apps.billing.services.billing_service import BillingService

User = get_user_model()


@pytest.fixture
def finance_user(db):
    return User.objects.create_user(
        email="financeiro@test.gw",
        password="Fin@12345",
        first_name="Ana",
        last_name="Financeiro",
        role=UserRole.FINANCEIRO,
    )


@pytest.fixture
def servico_consulta(db):
    return Servico.objects.create(
        codigo="CONS-001",
        nome="Consulta Geral",
        categoria="CONSULTA",
        preco=Decimal("5000.00"),
        preco_confirmado=True,
    )


@pytest.fixture
def patient_for_billing(db, receptionist_user):
    from apps.patients.services.patient_service import PatientService

    return PatientService.create(
        {
            "first_name": "Billing",
            "last_name": "Paciente",
            "birth_date": __import__("datetime").date(1988, 3, 15),
            "gender": "F",
            "phone": "+245955000333",
            "document_number": "BILL001",
            "document_type": "BI",
        },
        user=receptionist_user,
    )


@pytest.mark.django_db
class TestBillingModelo:
    def test_numero_orcamento(self, finance_user, patient_for_billing, servico_consulta):
        orcamento = BillingService.criar_orcamento(
            patient_for_billing.pk,
            finance_user,
            itens=[{"servico_id": servico_consulta.pk, "quantidade": 1}],
        )
        assert orcamento.numero.startswith("ORC-")
        assert orcamento.total == Decimal("5000.00")


@pytest.mark.django_db
class TestBillingServico:
    def test_fluxo_completo(self, finance_user, patient_for_billing, servico_consulta):
        orcamento = BillingService.criar_orcamento(
            patient_for_billing.pk,
            finance_user,
            itens=[{"servico_id": servico_consulta.pk, "quantidade": 2}],
        )
        BillingService.aprovar_orcamento(orcamento.pk, finance_user)
        fatura = BillingService.gerar_fatura(finance_user, orcamento_id=orcamento.pk)
        assert fatura.numero.startswith("FAT-")
        assert fatura.total == Decimal("10000.00")

        pagamento = BillingService.registar_pagamento(
            fatura.pk,
            finance_user,
            valor=Decimal("10000.00"),
            metodo_pagamento="DINHEIRO",
        )
        BillingService.confirmar_pagamento(pagamento.pk, finance_user)
        fatura.refresh_from_db()
        assert fatura.estado == FaturaEstado.PAGA
        assert Recibo.objects.filter(pagamento=pagamento).exists()

    def test_nao_edita_fatura_paga(self, finance_user, patient_for_billing, servico_consulta):
        fatura = BillingService.gerar_fatura(
            finance_user,
            paciente_id=patient_for_billing.pk,
            itens=[{"servico_id": servico_consulta.pk, "quantidade": 1}],
        )
        pagamento = BillingService.registar_pagamento(
            fatura.pk, finance_user, valor=fatura.total, metodo_pagamento="DINHEIRO"
        )
        BillingService.confirmar_pagamento(pagamento.pk, finance_user)
        with pytest.raises(ValueError, match="paga"):
            BillingService.adicionar_item_fatura(
                fatura.pk, finance_user, {"servico_id": servico_consulta.pk}
            )


@pytest.mark.django_db
class TestBillingAPI:
    def test_criar_servico(self, api_client, finance_user, seed_rbac):
        api_client.force_authenticate(user=finance_user)
        response = api_client.post(
            "/api/v1/billing/services/",
            {
                "codigo": "EX-001",
                "nome": "Hemograma",
                "categoria": "EXAME",
                "preco": "3500.00",
            },
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED

    def test_fluxo_orcamento_fatura(self, api_client, finance_user, patient_for_billing, servico_consulta, seed_rbac):
        api_client.force_authenticate(user=finance_user)
        quote_resp = api_client.post(
            "/api/v1/billing/quotes/",
            {
                "paciente": patient_for_billing.pk,
                "itens": [{"servico": servico_consulta.pk, "quantidade": 1}],
            },
            format="json",
        )
        assert quote_resp.status_code == status.HTTP_201_CREATED
        quote_id = quote_resp.data["data"]["id"]
        api_client.post(f"/api/v1/billing/quotes/{quote_id}/approve/")
        invoice_resp = api_client.post(
            "/api/v1/billing/invoices/",
            {"orcamento": quote_id},
            format="json",
        )
        assert invoice_resp.status_code == status.HTTP_201_CREATED
        invoice_id = invoice_resp.data["data"]["id"]
        pay_resp = api_client.post(
            "/api/v1/billing/payments/",
            {
                "fatura": invoice_id,
                "metodo_pagamento": "DINHEIRO",
                "valor": "5000.00",
            },
            format="json",
        )
        assert pay_resp.status_code == status.HTTP_201_CREATED
        pay_id = pay_resp.data["data"]["id"]
        confirm_resp = api_client.post(f"/api/v1/billing/payments/{pay_id}/confirm/")
        assert confirm_resp.status_code == 200
        assert confirm_resp.data["data"]["estado"] == PagamentoEstado.CONFIRMADO
        assert AuditLog.objects.filter(action=AuditAction.RECIBO_EMITIDO).exists()


@pytest.mark.django_db
class TestBillingRBAC:
    def test_rececionista_acesso_servicos(self, api_client, receptionist_user, seed_rbac):
        api_client.force_authenticate(user=receptionist_user)
        response = api_client.get("/api/v1/billing/services/")
        assert response.status_code == status.HTTP_200_OK

    def test_rececionista_sem_finance(self, api_client, receptionist_user, seed_rbac):
        api_client.force_authenticate(user=receptionist_user)
        response = api_client.get("/api/v1/finance/expenses/")
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestBillingDashboard:
    def test_dashboard_financeiro(self, finance_user, patient_for_billing, servico_consulta):
        BillingService.gerar_fatura(
            finance_user,
            paciente_id=patient_for_billing.pk,
            itens=[{"servico_id": servico_consulta.pk, "quantidade": 1}],
        )
        summary = BillingService.get_dashboard_summary()
        assert "indicadores" in summary
        assert summary["indicadores"]["faturas_pendentes"] >= 1


@pytest.mark.django_db
class TestBillingHistorico:
    def test_historico_paciente(self, finance_user, patient_for_billing, servico_consulta):
        BillingService.gerar_fatura(
            finance_user,
            paciente_id=patient_for_billing.pk,
            itens=[{"servico_id": servico_consulta.pk, "quantidade": 1}],
        )
        historico = BillingService.historico_financeiro(patient_for_billing.pk)
        assert historico["paciente_id"] == patient_for_billing.pk
        assert len(historico["faturas"]) == 1
