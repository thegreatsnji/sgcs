"""Testes Sprint 18.2 — Catálogo SauVida V1, recibo e legado."""

import json
from decimal import Decimal
from pathlib import Path

import pytest
from django.core.management import call_command

from apps.billing.constants import CATALOGO_VERSAO_ATIVA, CATALOGO_VERSAO_LEGADO
from apps.billing.models import Servico
from apps.billing.services.billing_service import BillingService
from apps.billing.services.receipt_print_service import build_receipt_print_context

RELEASES = Path(__file__).resolve().parents[3] / "data" / "releases"


@pytest.fixture
def patient_for_billing(db, receptionist_user):
    from apps.patients.services.patient_service import PatientService

    return PatientService.create(
        {
            "first_name": "S182",
            "last_name": "Paciente",
            "birth_date": __import__("datetime").date(1990, 1, 1),
            "gender": "M",
            "phone": "+245955000999",
            "document_number": "S182001",
            "document_type": "BI",
        },
        user=receptionist_user,
    )


@pytest.mark.django_db
class TestCatalogoV1Freeze:
    def test_release_files_exist(self):
        assert (RELEASES / "catalogo_sauvida_v1.csv").is_file()
        manifest = json.loads((RELEASES / "catalogo_sauvida_v1_manifest.json").read_text(encoding="utf-8"))
        assert manifest["versao_catalogo"] == "SAUVIDA_V1"
        assert manifest["servicos"] >= 119

    def test_operacional_exige_versao_v1(self, api_client, receptionist_user, seed_rbac):
        Servico.objects.create(
            codigo="LEG-1",
            nome="Legado",
            categoria="CONSULTA",
            preco=Decimal("1000"),
            preco_confirmado=True,
            versao_catalogo=CATALOGO_VERSAO_LEGADO,
            arquivado=True,
        )
        Servico.objects.create(
            codigo="V1-1",
            nome="V1",
            categoria="CONSULTA",
            preco=Decimal("1000"),
            preco_confirmado=True,
            versao_catalogo=CATALOGO_VERSAO_ATIVA,
        )
        api_client.force_authenticate(user=receptionist_user)
        r = api_client.get("/api/v1/billing/services/?operacional=1")
        codes = {x["codigo"] for x in r.data["data"]["results"]}
        assert "V1-1" in codes
        assert "LEG-1" not in codes


@pytest.mark.django_db
class TestPagamentoParcialSaldo:
    def test_saldo_nao_e_desconto(self, receptionist_user, patient_for_billing, seed_rbac):
        servico = Servico.objects.create(
            codigo="PP-1",
            nome="S",
            categoria="CONSULTA",
            preco=Decimal("10000"),
            preco_confirmado=True,
            versao_catalogo=CATALOGO_VERSAO_ATIVA,
        )
        fatura = BillingService.gerar_fatura(
            receptionist_user,
            paciente_id=patient_for_billing.pk,
            itens=[{"servico_id": servico.pk, "quantidade": 1}],
        )
        assert fatura.desconto == Decimal("0")
        assert fatura.total == Decimal("10000")
        p1 = BillingService.registar_pagamento(
            fatura.pk, receptionist_user, valor=Decimal("6000"), metodo_pagamento="DINHEIRO"
        )
        BillingService.confirmar_pagamento(p1.pk, receptionist_user)
        fatura.refresh_from_db()
        assert fatura.estado == "PARCIAL"
        assert fatura.total_pago == Decimal("6000")
        item = fatura.itens.get()
        assert item.valor_reducao == Decimal("0")


@pytest.mark.django_db
class TestReciboImpressao:
    def test_contexto_recibo_sauvida(self, receptionist_user, patient_for_billing, seed_rbac):
        servico = Servico.objects.create(
            codigo="REC-V1",
            nome="Consulta",
            categoria="CONSULTA",
            preco=Decimal("3000"),
            preco_confirmado=True,
            versao_catalogo=CATALOGO_VERSAO_ATIVA,
        )
        fatura = BillingService.gerar_fatura(
            receptionist_user,
            paciente_id=patient_for_billing.pk,
            itens=[{"servico_id": servico.pk, "quantidade": 1}],
        )
        pag = BillingService.registar_pagamento(
            fatura.pk, receptionist_user, valor=Decimal("3000"), metodo_pagamento="DINHEIRO"
        )
        BillingService.confirmar_pagamento(pag.pk, receptionist_user)
        recibo = pag.recibo
        ctx = build_receipt_print_context(recibo)
        assert ctx["textos"]["importancia_de"] == "Importância de"
        assert ctx["exator"]["nome"]
        assert ctx["recibo"]["numero_livro"]["ano"]


@pytest.mark.django_db
class TestArchiveLegacy:
    def test_archive_legacy_dry_run(self, db):
        Servico.objects.create(codigo="OLD", nome="Old", categoria="CONSULTA", preco=1)
        call_command("archive_legacy_catalog", "--dry-run")
