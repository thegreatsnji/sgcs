"""Testes — hardening faturação Receção (overpay, filtros, cancelar)."""

from decimal import Decimal

import pytest
from rest_framework import status

from apps.billing.constants import CATALOGO_VERSAO_ATIVA, FaturaEstado, MotivoReducao
from apps.billing.models import Servico
from apps.billing.services.billing_service import BillingService
from apps.settings.models import ConfiguracaoFaturacao
from apps.settings.services.settings_service import SettingsService


@pytest.fixture
def patient_billing(db, receptionist_user):
    from apps.patients.services.patient_service import PatientService

    return PatientService.create(
        {
            "first_name": "Fatima",
            "last_name": "Billing",
            "birth_date": __import__("datetime").date(1992, 4, 10),
            "gender": "F",
            "phone": "+245955777888",
            "document_number": "HARD-BILL-001",
            "document_type": "BI",
        },
        user=receptionist_user,
        emergency_contacts=[
            {
                "name": "Contacto",
                "phone": "+245955111000",
                "relationship": "CONJUGE",
                "is_primary": True,
            }
        ],
    )


@pytest.fixture
def servico_10k(db):
    return Servico.objects.create(
        codigo="HARD-10K",
        nome="Consulta hardening",
        categoria="CONSULTA",
        preco=Decimal("10000"),
        preco_confirmado=True,
        versao_catalogo=CATALOGO_VERSAO_ATIVA,
    )


def _fatura(user, patient, servico, *, preco_cobrado=None, motivo=None):
    item = {"servico_id": servico.pk, "quantidade": 1}
    if preco_cobrado is not None:
        item["preco_cobrado"] = preco_cobrado
        item["motivo_reducao"] = motivo or MotivoReducao.DIFICULDADE_FINANCEIRA
    return BillingService.gerar_fatura(user, paciente_id=patient.pk, itens=[item])


@pytest.mark.django_db
class TestOverpaymentGuard:
    def test_pagamento_exacto_saldo(self, receptionist_user, patient_billing, servico_10k):
        fatura = _fatura(receptionist_user, patient_billing, servico_10k)
        p = BillingService.registar_pagamento(
            fatura.pk, receptionist_user, valor=Decimal("10000"), metodo_pagamento="DINHEIRO"
        )
        BillingService.confirmar_pagamento(p.pk, receptionist_user)
        fatura.refresh_from_db()
        assert fatura.estado == FaturaEstado.PAGA
        assert fatura.total_pago == Decimal("10000")

    def test_parcial_depois_exacto(self, receptionist_user, patient_billing, servico_10k):
        fatura = _fatura(receptionist_user, patient_billing, servico_10k)
        p1 = BillingService.registar_pagamento(
            fatura.pk, receptionist_user, valor=Decimal("6000"), metodo_pagamento="DINHEIRO"
        )
        BillingService.confirmar_pagamento(p1.pk, receptionist_user)
        p2 = BillingService.registar_pagamento(
            fatura.pk, receptionist_user, valor=Decimal("4000"), metodo_pagamento="DINHEIRO"
        )
        BillingService.confirmar_pagamento(p2.pk, receptionist_user)
        fatura.refresh_from_db()
        assert fatura.estado == FaturaEstado.PAGA
        assert fatura.total_pago == Decimal("10000")

    def test_overpayment_recusado(self, receptionist_user, patient_billing, servico_10k):
        fatura = _fatura(receptionist_user, patient_billing, servico_10k)
        p1 = BillingService.registar_pagamento(
            fatura.pk, receptionist_user, valor=Decimal("6000"), metodo_pagamento="DINHEIRO"
        )
        BillingService.confirmar_pagamento(p1.pk, receptionist_user)
        with pytest.raises(ValueError, match="superior ao saldo"):
            BillingService.registar_pagamento(
                fatura.pk, receptionist_user, valor=Decimal("5000"), metodo_pagamento="DINHEIRO"
            )

    def test_zero_e_negativo_recusados(self, receptionist_user, patient_billing, servico_10k):
        fatura = _fatura(receptionist_user, patient_billing, servico_10k)
        with pytest.raises(ValueError, match="positivo"):
            BillingService.registar_pagamento(
                fatura.pk, receptionist_user, valor=Decimal("0"), metodo_pagamento="DINHEIRO"
            )
        with pytest.raises(ValueError, match="positivo"):
            BillingService.registar_pagamento(
                fatura.pk, receptionist_user, valor=Decimal("-100"), metodo_pagamento="DINHEIRO"
            )

    def test_pendente_reserva_saldo(self, receptionist_user, patient_billing, servico_10k):
        fatura = _fatura(receptionist_user, patient_billing, servico_10k)
        BillingService.registar_pagamento(
            fatura.pk, receptionist_user, valor=Decimal("7000"), metodo_pagamento="DINHEIRO"
        )
        with pytest.raises(ValueError, match="superior ao saldo"):
            BillingService.registar_pagamento(
                fatura.pk, receptionist_user, valor=Decimal("4000"), metodo_pagamento="DINHEIRO"
            )

    def test_reducao_parcial_overpay(self, receptionist_user, patient_billing, servico_10k):
        cfg = SettingsService._get_singleton(ConfiguracaoFaturacao)
        cfg.permitir_reducao_rececao = True
        cfg.limite_reducao_rececao_percentual = Decimal("50")
        cfg.exigir_motivo_reducao = True
        cfg.save()

        fatura = _fatura(
            receptionist_user,
            patient_billing,
            servico_10k,
            preco_cobrado=Decimal("8000"),
        )
        assert fatura.total == Decimal("8000")
        p1 = BillingService.registar_pagamento(
            fatura.pk, receptionist_user, valor=Decimal("5000"), metodo_pagamento="DINHEIRO"
        )
        BillingService.confirmar_pagamento(p1.pk, receptionist_user)
        with pytest.raises(ValueError, match="superior ao saldo"):
            BillingService.registar_pagamento(
                fatura.pk, receptionist_user, valor=Decimal("4000"), metodo_pagamento="DINHEIRO"
            )
        p2 = BillingService.registar_pagamento(
            fatura.pk, receptionist_user, valor=Decimal("3000"), metodo_pagamento="DINHEIRO"
        )
        BillingService.confirmar_pagamento(p2.pk, receptionist_user)
        fatura.refresh_from_db()
        assert fatura.estado == FaturaEstado.PAGA


@pytest.mark.django_db
class TestInvoiceFiltersAndCancel:
    def test_search_e_com_saldo(self, api_client, receptionist_user, patient_billing, servico_10k):
        fatura = _fatura(receptionist_user, patient_billing, servico_10k)
        p1 = BillingService.registar_pagamento(
            fatura.pk, receptionist_user, valor=Decimal("6000"), metodo_pagamento="DINHEIRO"
        )
        BillingService.confirmar_pagamento(p1.pk, receptionist_user)

        api_client.force_authenticate(user=receptionist_user)
        by_name = api_client.get("/api/v1/billing/invoices/", {"search": "Fatima"})
        assert by_name.status_code == 200
        assert any(r["id"] == fatura.pk for r in by_name.data["data"]["results"])

        by_num = api_client.get("/api/v1/billing/invoices/", {"search": fatura.numero})
        assert any(r["id"] == fatura.pk for r in by_num.data["data"]["results"])

        pending = api_client.get("/api/v1/billing/invoices/", {"com_saldo": True})
        assert pending.status_code == 200
        ids = {r["id"] for r in pending.data["data"]["results"]}
        assert fatura.pk in ids
        row = next(r for r in pending.data["data"]["results"] if r["id"] == fatura.pk)
        assert Decimal(row["saldo"]) == Decimal("4000")

    def test_filtro_periodo_hoje(self, api_client, receptionist_user, patient_billing, servico_10k):
        fatura = _fatura(receptionist_user, patient_billing, servico_10k)
        api_client.force_authenticate(user=receptionist_user)
        r = api_client.get("/api/v1/billing/invoices/", {"periodo": "hoje"})
        assert r.status_code == 200
        assert any(x["id"] == fatura.pk for x in r.data["data"]["results"])

    def test_cancelar_fatura_ui_api(self, api_client, receptionist_user, patient_billing, servico_10k):
        fatura = _fatura(receptionist_user, patient_billing, servico_10k)
        api_client.force_authenticate(user=receptionist_user)
        r = api_client.post(f"/api/v1/billing/invoices/{fatura.pk}/cancel/")
        assert r.status_code == 200
        fatura.refresh_from_db()
        assert fatura.estado == FaturaEstado.CANCELADA

        pending = api_client.get("/api/v1/billing/invoices/", {"com_saldo": True})
        assert fatura.pk not in {x["id"] for x in pending.data["data"]["results"]}

        resumo = api_client.get("/api/v1/billing/resumo-operacional/", {"periodo": "hoje"})
        assert resumo.status_code == 200
        assert Decimal(resumo.data["data"]["saldo_pendente"]) == Decimal("0.00")

    def test_cancelar_paga_recusado(self, api_client, receptionist_user, patient_billing, servico_10k):
        fatura = _fatura(receptionist_user, patient_billing, servico_10k)
        p = BillingService.registar_pagamento(
            fatura.pk, receptionist_user, valor=Decimal("10000"), metodo_pagamento="DINHEIRO"
        )
        BillingService.confirmar_pagamento(p.pk, receptionist_user)
        api_client.force_authenticate(user=receptionist_user)
        r = api_client.post(f"/api/v1/billing/invoices/{fatura.pk}/cancel/")
        assert r.status_code == status.HTTP_400_BAD_REQUEST
