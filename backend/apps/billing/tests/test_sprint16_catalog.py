"""Testes Sprint 16 — catálogo SauVida."""

from decimal import Decimal
from io import StringIO

import pytest
from django.core.management import call_command
from rest_framework import status

from apps.authentication.models import UserRole
from apps.billing.constants import PRICE_REVIEW_MARKER
from apps.billing.models import Servico, ServicoPrecoHistorico
from apps.billing.services.catalog_service import parse_preco_fcfa, user_pode_alterar_preco
from apps.settings.models import Departamento, EspecialidadeMedica


@pytest.mark.django_db
class TestCatalogoServico:
    def test_codigo_unico(self, db):
        Servico.objects.create(codigo="U-1", nome="A", categoria="CONSULTA", preco=Decimal("100"))
        with pytest.raises(Exception):
            Servico.objects.create(codigo="U-1", nome="B", categoria="CONSULTA", preco=Decimal("200"))

    def test_preco_nao_negativo_serializer(self, api_client, admin_user, seed_rbac):
        api_client.force_authenticate(user=admin_user)
        response = api_client.post(
            "/api/v1/billing/services/",
            {
                "codigo": "NEG-1",
                "nome": "Teste",
                "categoria": "CONSULTA",
                "preco": "-1",
            },
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_rececionista_nao_altera_preco(self, api_client, receptionist_user, seed_rbac):
        servico = Servico.objects.create(
            codigo="P-1", nome="Preço", categoria="CONSULTA", preco=Decimal("5000"), preco_confirmado=True
        )
        api_client.force_authenticate(user=receptionist_user)
        response = api_client.patch(
            f"/api/v1/billing/services/{servico.pk}/",
            {"preco": "6000"},
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_admin_altera_preco_com_historico(self, api_client, admin_user, seed_rbac):
        servico = Servico.objects.create(
            codigo="P-2", nome="Preço", categoria="CONSULTA", preco=Decimal("5000"), preco_confirmado=True
        )
        api_client.force_authenticate(user=admin_user)
        response = api_client.patch(
            f"/api/v1/billing/services/{servico.pk}/",
            {"preco": "7000"},
            format="json",
        )
        assert response.status_code == 200
        assert ServicoPrecoHistorico.objects.filter(servico=servico).exists()

    def test_item_fatura_preserva_preco(self, finance_user, patient_for_billing, seed_rbac):
        from apps.billing.services.billing_service import BillingService

        servico = Servico.objects.create(
            codigo="HIST-1", nome="Hist", categoria="CONSULTA", preco=Decimal("10000"), preco_confirmado=True
        )
        fatura = BillingService.gerar_fatura(
            finance_user,
            paciente_id=patient_for_billing.pk,
            itens=[{"servico_id": servico.pk, "quantidade": 1}],
        )
        item_preco = fatura.itens.first().preco
        servico.preco = Decimal("20000")
        servico.save()
        fatura.refresh_from_db()
        assert fatura.itens.first().preco == item_preco

    def test_lista_operacional_exclui_inactivos(self, api_client, receptionist_user, seed_rbac):
        Servico.objects.create(
            codigo="OFF-1", nome="Off", categoria="CONSULTA", preco=Decimal("1"), activo=False
        )
        Servico.objects.create(
            codigo="ON-1",
            nome="On",
            categoria="CONSULTA",
            preco=Decimal("1"),
            activo=True,
            preco_confirmado=True,
            versao_catalogo="SAUVIDA_V1",
        )
        api_client.force_authenticate(user=receptionist_user)
        response = api_client.get("/api/v1/billing/services/?operacional=1&activo=true")
        assert response.status_code == 200
        codes = {r["codigo"] for r in response.data["data"]["results"]}
        assert "ON-1" in codes
        assert "OFF-1" not in codes


@pytest.mark.django_db
class TestImportCatalogo:
    def test_parse_preco_revisar(self):
        assert parse_preco_fcfa(PRICE_REVIEW_MARKER)[1] is True
        assert parse_preco_fcfa("")[1] is True
        preco, ok = parse_preco_fcfa("15000")
        assert ok is False
        assert preco == Decimal("15000")

    def test_dry_run_pendentes(self, db, seed_rbac):
        Departamento.objects.create(codigo="CONS-GER", nome="Consulta Geral")
        out = StringIO()
        call_command("import_catalogo_sauvida", "--dry-run", stdout=out)
        assert "Pendentes revisão:" in out.getvalue()

    def test_import_com_preco(self, db, seed_rbac, tmp_path):
        Departamento.objects.create(codigo="LAB", nome="Laboratório")
        csv_path = tmp_path / "one.csv"
        csv_path.write_text(
            "codigo,nome,categoria,departamento,especialidade,preco_fcfa,ativo,"
            "exige_pedido_medico,exige_pagamento_antecipado,permite_pagamento_parcial,"
            "exige_agendamento,gera_resultado,duracao_minutos,observacoes\n"
            "T-1,Teste,Laboratório,LAB,,10000,1,0,0,1,0,1,0,\n",
            encoding="utf-8",
        )
        call_command("import_catalogo_sauvida", f"--file={csv_path}", "--apply")
        assert Servico.objects.filter(codigo="T-1", preco=Decimal("10000")).exists()


@pytest.fixture
def finance_user(db):
    from django.contrib.auth import get_user_model

    User = get_user_model()
    return User.objects.create_user(
        email="fin16@test.gw",
        password="Fin@12345",
        first_name="Fin",
        last_name="Test",
        role=UserRole.FINANCEIRO,
    )


@pytest.fixture
def patient_for_billing(db, receptionist_user):
    from apps.patients.services.patient_service import PatientService

    return PatientService.create(
        {
            "first_name": "Cat",
            "last_name": "Paciente",
            "birth_date": __import__("datetime").date(1990, 1, 1),
            "gender": "F",
            "phone": "+245955000111",
            "document_number": "CAT001",
            "document_type": "BI",
        },
        user=receptionist_user,
    )
