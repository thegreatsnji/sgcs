"""Testes do módulo financeiro — Sprint 8 Fase 2."""

from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status

from apps.audit_logs.models import AuditAction, AuditLog
from apps.authentication.models import UserRole
from apps.billing.services.billing_service import BillingService
from apps.finance.constants import CaixaEstado, DespesaEstado, MovimentoTipo
from apps.finance.models import Caixa, MovimentoFinanceiro
from apps.finance.services.finance_service import FinanceService

User = get_user_model()


@pytest.fixture
def finance_user(db):
    return User.objects.create_user(
        email="financeiro2@test.gw",
        password="Fin@12345",
        first_name="Carlos",
        last_name="Tesouraria",
        role=UserRole.FINANCEIRO,
    )


@pytest.fixture
def caixa_principal(db):
    return Caixa.objects.create(codigo="CAIXA-TEST", nome="Caixa Teste")


@pytest.fixture
def servico_consulta(db):
    from apps.billing.models import Servico

    return Servico.objects.create(
        codigo="CONS-FIN",
        nome="Consulta Financeira",
        categoria="CONSULTA",
        preco=Decimal("3000.00"),
    )


@pytest.fixture
def patient_fin(db, receptionist_user):
    from apps.patients.services.patient_service import PatientService

    return PatientService.create(
        {
            "first_name": "Finance",
            "last_name": "Patient",
            "birth_date": __import__("datetime").date(1990, 1, 1),
            "gender": "M",
            "phone": "+245955000444",
            "document_number": "FINP001",
            "document_type": "BI",
        },
        user=receptionist_user,
    )


@pytest.mark.django_db
class TestFinanceCaixa:
    def test_abrir_fechar_caixa(self, finance_user, caixa_principal):
        caixa = FinanceService.abrir_caixa(
            caixa_principal.pk, finance_user, saldo_inicial=Decimal("1000.00")
        )
        assert caixa.estado == CaixaEstado.ABERTO
        assert caixa.saldo_actual == Decimal("1000.00")
        caixa = FinanceService.fechar_caixa(caixa_principal.pk, finance_user)
        assert caixa.estado == CaixaEstado.FECHADO
        assert AuditLog.objects.filter(action=AuditAction.CAIXA_ABERTA).exists()


@pytest.mark.django_db
class TestFinanceMovimentos:
    def test_movimento_manual(self, finance_user, caixa_principal):
        FinanceService.abrir_caixa(caixa_principal.pk, finance_user, saldo_inicial=Decimal("500"))
        mov = FinanceService.criar_movimento(
            finance_user,
            caixa_id=caixa_principal.pk,
            tipo=MovimentoTipo.ENTRADA,
            origem="MANUAL",
            valor=Decimal("200"),
            descricao="Entrada manual",
        )
        caixa_principal.refresh_from_db()
        assert caixa_principal.saldo_actual == Decimal("700.00")
        assert mov.pk is not None


@pytest.mark.django_db
class TestFinanceDespesas:
    def test_workflow_despesa(self, finance_user, caixa_principal):
        FinanceService.abrir_caixa(caixa_principal.pk, finance_user, saldo_inicial=Decimal("10000"))
        despesa = FinanceService.criar_despesa(
            finance_user,
            {
                "fornecedor": "Fornecedor X",
                "valor": Decimal("1500"),
                "descricao": "Material clínico",
                "data": __import__("datetime").date.today(),
                "categoria": "MATERIAL_CLINICO",
            },
        )
        FinanceService.aprovar_despesa(despesa.pk, finance_user)
        FinanceService.pagar_despesa(despesa.pk, finance_user)
        despesa.refresh_from_db()
        assert despesa.estado == DespesaEstado.PAGA
        caixa_principal.refresh_from_db()
        assert caixa_principal.saldo_actual == Decimal("8500.00")


@pytest.mark.django_db
class TestFinanceBillingIntegracao:
    def test_pagamento_cria_movimento(
        self, finance_user, patient_fin, servico_consulta, caixa_principal
    ):
        FinanceService.abrir_caixa(caixa_principal.pk, finance_user, saldo_inicial=Decimal("0"))
        fatura = BillingService.gerar_fatura(
            finance_user,
            paciente_id=patient_fin.pk,
            itens=[{"servico_id": servico_consulta.pk, "quantidade": 1}],
        )
        pagamento = BillingService.registar_pagamento(
            fatura.pk, finance_user, valor=fatura.total, metodo_pagamento="DINHEIRO"
        )
        BillingService.confirmar_pagamento(pagamento.pk, finance_user)
        assert MovimentoFinanceiro.objects.filter(pagamento_id=pagamento.pk).exists()
        assert AuditLog.objects.filter(action=AuditAction.MOVIMENTO_FINANCEIRO).exists()


@pytest.mark.django_db
class TestFinanceAPI:
    def test_listar_caixas(self, api_client, finance_user, caixa_principal, seed_rbac):
        api_client.force_authenticate(user=finance_user)
        response = api_client.get("/api/v1/finance/cash-registers/")
        assert response.status_code == 200

    def test_criar_despesa_api(self, api_client, finance_user, seed_rbac):
        api_client.force_authenticate(user=finance_user)
        response = api_client.post(
            "/api/v1/finance/expenses/",
            {
                "fornecedor": "Energia SA",
                "valor": "2500.00",
                "descricao": "Conta de luz",
                "data": str(__import__("datetime").date.today()),
                "categoria": "ENERGIA",
            },
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED

    def test_relatorio_diario(self, api_client, finance_user, seed_rbac):
        api_client.force_authenticate(user=finance_user)
        response = api_client.get("/api/v1/finance/reports/daily/")
        assert response.status_code == 200
        assert "receitas" in response.data["data"]

    def test_dashboard_financeiro(self, api_client, finance_user, seed_rbac):
        api_client.force_authenticate(user=finance_user)
        response = api_client.get("/api/v1/dashboard/finance/")
        assert response.status_code == 200


@pytest.mark.django_db
class TestFinanceRBAC:
    def test_medico_sem_acesso(self, api_client, receptionist_user, seed_rbac):
        api_client.force_authenticate(user=receptionist_user)
        response = api_client.get("/api/v1/finance/cash-registers/")
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestFinanceDashboard:
    def test_fluxo_caixa(self, finance_user, caixa_principal):
        FinanceService.abrir_caixa(caixa_principal.pk, finance_user, saldo_inicial=Decimal("100"))
        fluxo = FinanceService.calcular_fluxo_caixa()
        assert "receitas_hoje" in fluxo
        summary = FinanceService.get_dashboard_summary()
        assert "indicadores" in summary
