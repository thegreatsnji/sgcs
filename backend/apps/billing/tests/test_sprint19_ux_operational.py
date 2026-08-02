"""Sprint 19 — regressão operacional e contratos estáveis (UX / piloto)."""

from decimal import Decimal

import pytest
from rest_framework import status

from apps.billing.constants import CATALOGO_VERSAO_ATIVA
from apps.billing.models import Servico


@pytest.fixture
def patient_for_billing(db, receptionist_user):
    from apps.patients.services.patient_service import PatientService

    return PatientService.create(
        {
            "first_name": "S19",
            "last_name": "Utente",
            "birth_date": __import__("datetime").date(1992, 5, 5),
            "gender": "F",
            "phone": "+245955000111",
            "document_number": "S19001",
            "document_type": "BI",
        },
        user=receptionist_user,
    )


@pytest.fixture
def servico_v1_operacional(db):
    return Servico.objects.create(
        codigo="UX-LAB-GLICOSE",
        nome="Glicose (teste UX)",
        categoria="LABORATORIO",
        preco=Decimal("1500"),
        preco_confirmado=True,
        versao_catalogo=CATALOGO_VERSAO_ATIVA,
        activo=True,
        arquivado=False,
    )


@pytest.mark.django_db
class TestCatalogoOperacionalFilter:
    def test_servico_v1_aparece_operacional(self, servico_v1_operacional):
        qs = Servico.objects.filter(
            versao_catalogo=CATALOGO_VERSAO_ATIVA,
            activo=True,
            arquivado=False,
            preco_confirmado=True,
        )
        assert qs.filter(pk=servico_v1_operacional.pk).exists()


@pytest.mark.django_db
class TestReceptionApiSmoke:
    def test_dashboard_reception(self, api_client, receptionist_user, seed_rbac):
        api_client.force_authenticate(user=receptionist_user)
        r = api_client.get("/api/v1/dashboard/reception/")
        assert r.status_code == status.HTTP_200_OK
        body = r.data.get("data", r.data)
        assert "cards" in body

    def test_queue_list(self, api_client, receptionist_user, seed_rbac):
        api_client.force_authenticate(user=receptionist_user)
        r = api_client.get("/api/v1/reception/queue/")
        assert r.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestBillingServicesOperacional:
    def test_list_operacional(self, api_client, receptionist_user, seed_rbac, servico_v1_operacional):
        api_client.force_authenticate(user=receptionist_user)
        r = api_client.get("/api/v1/billing/services/", {"operacional": "1", "page_size": 50})
        assert r.status_code == status.HTTP_200_OK
        payload = r.data["data"]
        codes = {row["codigo"] for row in payload["results"]}
        assert servico_v1_operacional.codigo in codes

    def test_search_operacional_por_nome(
        self, api_client, receptionist_user, seed_rbac, servico_v1_operacional
    ):
        api_client.force_authenticate(user=receptionist_user)
        r = api_client.get(
            "/api/v1/billing/services/",
            {"operacional": "1", "search": "Glicose", "page_size": 20},
        )
        assert r.status_code == status.HTTP_200_OK
        codes = {x["codigo"] for x in r.data["data"]["results"]}
        assert servico_v1_operacional.codigo in codes


@pytest.mark.django_db
class TestPatientsSearchPartial:
    def test_patients_list_search(self, api_client, receptionist_user, seed_rbac, patient_for_billing):
        api_client.force_authenticate(user=receptionist_user)
        term = patient_for_billing.first_name[:3]
        r = api_client.get("/api/v1/patients/", {"search": term, "page_size": 10})
        assert r.status_code == status.HTTP_200_OK
        ids = [p["id"] for p in r.data["data"]["results"]]
        assert patient_for_billing.pk in ids


class TestBillingDashboardSummary:
    def test_dashboard_summary_estrutura(self):
        from apps.billing.services.billing_service import BillingService

        data = BillingService.get_dashboard_summary()
        assert "indicadores" in data
        assert "receita_hoje" in data["indicadores"]


class TestItemFaturaReducaoMath:
    @pytest.mark.parametrize(
        "oficial,cobrado,esperado",
        [
            (Decimal("10000"), Decimal("10000"), Decimal("0")),
            (Decimal("10000"), Decimal("8000"), Decimal("2000")),
            (Decimal("5000"), Decimal("0"), Decimal("5000")),
        ],
    )
    def test_diferenca_reducao(self, oficial, cobrado, esperado):
        diff = max(Decimal("0"), oficial - cobrado)
        assert diff == esperado
