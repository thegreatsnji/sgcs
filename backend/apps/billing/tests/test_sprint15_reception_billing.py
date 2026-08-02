"""Testes Sprint 15 — RBAC receção, perfis demo e catálogo SauVida."""

from decimal import Decimal
from io import StringIO

import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command
from rest_framework import status

from apps.authentication.models import UserRole
from apps.billing.clinic_scope import EXCLUDED_SERVICE_CATEGORIES
from apps.billing.models import Servico
from apps.users.management.commands.seed_demo import DEMO_USERS

from apps.users.services.rbac_service import RBACService

User = get_user_model()


@pytest.fixture
def patient_for_billing(db, receptionist_user):
    from apps.patients.services.patient_service import PatientService

    return PatientService.create(
        {
            "first_name": "Billing",
            "last_name": "Paciente",
            "birth_date": __import__("datetime").date(1988, 3, 15),
            "gender": "F",
            "phone": "+245955000444",
            "document_number": "BILLREC001",
            "document_type": "BI",
        },
        user=receptionist_user,
    )


@pytest.fixture
def finance_user(db):
    return User.objects.create_user(
        email="financeiro-s15@test.gw",
        password="Fin@12345",
        first_name="Ana",
        last_name="Financeiro",
        role=UserRole.FINANCEIRO,
    )


@pytest.fixture
def director_user(db):
    return User.objects.create_user(
        email="director@test.gw",
        password="Director@123",
        first_name="Director",
        last_name="Teste",
        role=UserRole.DIRECTOR,
    )


@pytest.fixture
def medico_user(db):
    return User.objects.create_user(
        email="medico@test.gw",
        password="Medico@12345",
        first_name="Médico",
        last_name="Teste",
        role=UserRole.MEDICO,
    )


@pytest.fixture
def lab_user(db):
    return User.objects.create_user(
        email="lab@test.gw",
        password="Lab@12345",
        first_name="Lab",
        last_name="Teste",
        role=UserRole.LABORATORIO,
    )


@pytest.fixture
def servico_consulta(db):
    return Servico.objects.create(
        codigo="CONS-REC-001",
        nome="Consulta Receção",
        categoria="CONSULTA",
        preco=Decimal("5000.00"),
        preco_confirmado=True,
    )


@pytest.mark.django_db
class TestReceptionBillingRBAC:
    def test_rececionista_lista_faturas(self, api_client, receptionist_user, seed_rbac):
        api_client.force_authenticate(user=receptionist_user)
        assert api_client.get("/api/v1/billing/invoices/").status_code == status.HTTP_200_OK

    def test_rececionista_cria_fatura(
        self, api_client, receptionist_user, patient_for_billing, servico_consulta, seed_rbac
    ):
        api_client.force_authenticate(user=receptionist_user)
        response = api_client.post(
            "/api/v1/billing/invoices/",
            {
                "paciente": patient_for_billing.pk,
                "itens": [{"servico": servico_consulta.pk, "quantidade": 1}],
            },
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED

    def test_rececionista_regista_pagamento(
        self, api_client, receptionist_user, finance_user, patient_for_billing, servico_consulta, seed_rbac
    ):
        from apps.billing.services.billing_service import BillingService

        fatura = BillingService.gerar_fatura(
            finance_user,
            paciente_id=patient_for_billing.pk,
            itens=[{"servico_id": servico_consulta.pk, "quantidade": 1}],
        )
        api_client.force_authenticate(user=receptionist_user)
        pay_resp = api_client.post(
            "/api/v1/billing/payments/",
            {
                "fatura": fatura.pk,
                "metodo_pagamento": "DINHEIRO",
                "valor": str(fatura.total),
            },
            format="json",
        )
        assert pay_resp.status_code == status.HTTP_201_CREATED
        pay_id = pay_resp.data["data"]["id"]
        confirm = api_client.post(f"/api/v1/billing/payments/{pay_id}/confirm/")
        assert confirm.status_code == 200

    def test_rececionista_lista_recibos(self, api_client, receptionist_user, seed_rbac):
        api_client.force_authenticate(user=receptionist_user)
        assert api_client.get("/api/v1/billing/receipts/").status_code == status.HTTP_200_OK

    def test_rececionista_historico_paciente(
        self, api_client, receptionist_user, patient_for_billing, seed_rbac
    ):
        api_client.force_authenticate(user=receptionist_user)
        url = f"/api/v1/billing/patient-history/{patient_for_billing.pk}/"
        assert api_client.get(url).status_code == status.HTTP_200_OK

    def test_rececionista_nao_gerir_despesas(self, api_client, receptionist_user, seed_rbac):
        api_client.force_authenticate(user=receptionist_user)
        assert api_client.get("/api/v1/finance/expenses/").status_code == status.HTTP_403_FORBIDDEN

    def test_rececionista_nao_config_financeira(self, api_client, receptionist_user, seed_rbac):
        api_client.force_authenticate(user=receptionist_user)
        assert api_client.get("/api/v1/settings/billing/").status_code == status.HTTP_403_FORBIDDEN

    def test_medico_nao_confirma_pagamento(
        self, api_client, medico_user, finance_user, patient_for_billing, servico_consulta, seed_rbac
    ):
        from apps.billing.services.billing_service import BillingService

        fatura = BillingService.gerar_fatura(
            finance_user,
            paciente_id=patient_for_billing.pk,
            itens=[{"servico_id": servico_consulta.pk, "quantidade": 1}],
        )
        pagamento = BillingService.registar_pagamento(
            fatura.pk, finance_user, valor=fatura.total, metodo_pagamento="DINHEIRO"
        )
        api_client.force_authenticate(user=medico_user)
        response = api_client.post(f"/api/v1/billing/payments/{pagamento.pk}/confirm/")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_laboratorio_nao_regista_pagamento(
        self, api_client, lab_user, finance_user, patient_for_billing, servico_consulta, seed_rbac
    ):
        from apps.billing.services.billing_service import BillingService

        fatura = BillingService.gerar_fatura(
            finance_user,
            paciente_id=patient_for_billing.pk,
            itens=[{"servico_id": servico_consulta.pk, "quantidade": 1}],
        )
        api_client.force_authenticate(user=lab_user)
        response = api_client.post(
            "/api/v1/billing/payments/",
            {
                "fatura": fatura.pk,
                "metodo_pagamento": "DINHEIRO",
                "valor": str(fatura.total),
            },
            format="json",
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_director_relatorios_financeiros(self, api_client, director_user, seed_rbac):
        api_client.force_authenticate(user=director_user)
        assert api_client.get("/api/v1/reports/billing/").status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestSeedDemoProfiles:
    def test_seed_demo_cria_utilizador_por_perfil_rbac(self, db, seed_rbac):
        out = StringIO()
        call_command("seed_demo", stdout=out)
        roles = {spec["role"] for spec in DEMO_USERS}
        for role in roles:
            assert User.objects.filter(role=role).exists(), f"sem utilizador demo para {role}"
        assert User.objects.filter(email="enfermeiro@sauvida.gw", role=UserRole.ENFERMEIRO).exists()
        assert UserRole.FINANCEIRO not in roles
        assert not User.objects.filter(email="financeiro@sauvida.gw", is_active=True).exists()


@pytest.mark.django_db
class TestInternamentoCatalogo:
    def test_lista_servicos_exclui_internamento_por_defeito(self, api_client, receptionist_user, seed_rbac):
        Servico.objects.create(
            codigo="INT-TEST",
            nome="Diária teste",
            categoria="INTERNAMENTO",
            preco=Decimal("1.00"),
            activo=True,
        )
        Servico.objects.create(
            codigo="CONS-VIS",
            nome="Consulta visível",
            categoria="CONSULTA",
            preco=Decimal("1000.00"),
            activo=True,
        )
        api_client.force_authenticate(user=receptionist_user)
        response = api_client.get("/api/v1/billing/services/")
        assert response.status_code == status.HTTP_200_OK
        codes = {item["codigo"] for item in response.data["data"]["results"]}
        assert "CONS-VIS" in codes
        assert "INT-TEST" not in codes

    def test_import_ignora_categoria_internamento(self, db, tmp_path, seed_rbac):
        csv_path = tmp_path / "mini.csv"
        csv_path.write_text(
            "codigo,nome,descricao,categoria,preco,activo\n"
            "X-INT,Diária,desc,INTERNAMENTO,100,1\n"
            "X-OK,Consulta,desc,CONSULTA,100,1\n",
            encoding="utf-8",
        )
        call_command("import_servico_catalog", file=str(csv_path))
        assert not Servico.objects.filter(codigo="X-INT").exists()
        assert Servico.objects.filter(codigo="X-OK").exists()
        assert "INTERNAMENTO" in EXCLUDED_SERVICE_CATEGORIES


@pytest.mark.django_db
class TestReceptionRolePermissions:
    def test_rececionista_tem_billing_operacional(self, receptionist_user, seed_rbac):
        perms = RBACService.get_user_permissions(receptionist_user)
        assert "billing.view" in perms
        assert "billing.create" in perms
        assert "billing.payment" in perms
        assert "billing.receipt" in perms
        assert "finance.expense" not in perms
        assert "finance.view" not in perms
        assert "settings.featureflags" not in perms
