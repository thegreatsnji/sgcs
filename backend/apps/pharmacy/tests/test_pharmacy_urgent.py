import pytest
from django.contrib.auth import get_user_model

from apps.authentication.models import UserRole
from apps.pharmacy.models import MedicamentoUrgencia
from apps.pharmacy.services.stock_service import StockUrgenciaError, StockUrgenciaService


@pytest.fixture
def nurse_user(db, seed_rbac):
    User = get_user_model()
    return User.objects.create_user(
        email="enf@test.gw",
        password="TestPass123!",
        first_name="Enf",
        last_name="Teste",
        role=UserRole.ENFERMEIRO,
        is_active=True,
    )


@pytest.fixture
def med_urg(db):
    return MedicamentoUrgencia.objects.create(
        codigo="MEDU-TEST",
        nome="Teste Urgência",
        quantidade_stock=10,
        stock_minimo=5,
    )


@pytest.mark.django_db
class TestStockUrgenciaService:
    def test_entrada_aumenta_stock(self, med_urg, nurse_user):
        StockUrgenciaService.registar_movimento(
            med_urg, tipo="ENTRADA", quantidade=5, operador=nurse_user
        )
        med_urg.refresh_from_db()
        assert med_urg.quantidade_stock == 15

    def test_saida_insuficiente(self, med_urg, nurse_user):
        with pytest.raises(StockUrgenciaError):
            StockUrgenciaService.registar_movimento(
                med_urg, tipo="SAIDA", quantidade=100, operador=nurse_user
            )


@pytest.mark.django_db
class TestPharmacyApi:
    def test_list_requires_auth(self, api_client):
        r = api_client.get("/api/v1/pharmacy/urgent-medicines/")
        assert r.status_code in (401, 403)

    def test_nurse_can_list(self, api_client, nurse_user, med_urg):
        api_client.force_authenticate(user=nurse_user)
        r = api_client.get("/api/v1/pharmacy/urgent-medicines/")
        assert r.status_code == 200
        assert r.data["data"]["count"] >= 1

    def test_movimento_entrada(self, api_client, nurse_user, med_urg):
        api_client.force_authenticate(user=nurse_user)
        r = api_client.post(
            f"/api/v1/pharmacy/urgent-medicines/{med_urg.pk}/movimento/",
            {"tipo": "ENTRADA", "quantidade": 3, "motivo": "Reposição"},
            format="json",
        )
        assert r.status_code == 200
        med_urg.refresh_from_db()
        assert med_urg.quantidade_stock == 13
