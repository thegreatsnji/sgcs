import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from rest_framework.test import APIClient

from apps.authentication.models import UserRole
from apps.pharmacy.constants import CategoriaItemUrgencia
from apps.pharmacy.models import MedicamentoUrgencia, MovimentoStockUrgencia
from apps.pharmacy.services.stock_service import StockUrgenciaError, StockUrgenciaService
from apps.pharmacy.import_plan import (
    NAO_MANTER,
    PENDENTE_QUANTIDADE,
    QUANTIDADE_INVALIDA,
    UNIDADE_AUSENTE,
    VALIDO,
    build_import_plan,
)
from apps.pharmacy.status import estado_item

User = get_user_model()


@pytest.fixture
def nurse_user(db, seed_rbac):
    return User.objects.create_user(
        email="enf@test.gw",
        password="TestPass123!",
        first_name="Enf",
        last_name="Teste",
        role=UserRole.ENFERMEIRO,
        is_active=True,
    )


@pytest.fixture
def director_user(db, seed_rbac):
    return User.objects.create_user(
        email="dir@test.gw",
        password="TestPass123!",
        first_name="Dir",
        last_name="Teste",
        role=UserRole.DIRECTOR,
        is_active=True,
    )


@pytest.fixture
def doctor_user(db, seed_rbac):
    return User.objects.create_user(
        email="med@test.gw",
        password="TestPass123!",
        first_name="Med",
        last_name="Teste",
        role=UserRole.MEDICO,
        is_active=True,
    )


@pytest.fixture
def med_urg(db):
    return MedicamentoUrgencia.objects.create(
        codigo="MEDU-TEST",
        nome="Ceftriaxona teste",
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
        med_urg.refresh_from_db()
        assert med_urg.quantidade_stock == 10

    def test_nunca_negativo(self, med_urg, nurse_user):
        StockUrgenciaService.registar_movimento(
            med_urg, tipo="SAIDA", quantidade=10, operador=nurse_user
        )
        with pytest.raises(StockUrgenciaError):
            StockUrgenciaService.registar_movimento(
                med_urg, tipo="SAIDA", quantidade=1, operador=nurse_user
            )

    def test_criar_item_cria_movimento_inicial(self, nurse_user):
        item = StockUrgenciaService.criar_item(
            nome="Oxitocina",
            categoria=CategoriaItemUrgencia.MEDICAMENTO,
            unidade="ampola",
            quantidade_inicial=20,
            stock_minimo=5,
            operador=nurse_user,
        )
        assert item.quantidade_stock == 20
        mov = MovimentoStockUrgencia.objects.get(medicamento=item)
        assert mov.tipo == "ENTRADA"
        assert mov.origem == "STOCK_INICIAL"
        assert mov.operador == nurse_user

    def test_ajuste(self, med_urg, nurse_user):
        StockUrgenciaService.registar_movimento(
            med_urg, tipo="AJUSTE", quantidade=7, operador=nurse_user
        )
        med_urg.refresh_from_db()
        assert med_urg.quantidade_stock == 7

    def test_perda_expiracao(self, med_urg, nurse_user):
        StockUrgenciaService.registar_movimento(
            med_urg, tipo="PERDA_EXPIRACAO", quantidade=2, operador=nurse_user
        )
        med_urg.refresh_from_db()
        assert med_urg.quantidade_stock == 8

    def test_movimento_imutavel(self, med_urg, nurse_user):
        mov = StockUrgenciaService.registar_movimento(
            med_urg, tipo="ENTRADA", quantidade=1, operador=nurse_user
        )
        with pytest.raises(ValueError):
            mov.motivo = "x"
            mov.save()
        with pytest.raises(ValueError):
            mov.delete()


@pytest.mark.django_db
class TestEstados:
    def test_sem_stock(self):
        assert estado_item(quantidade=0, stock_minimo=5) == "SEM_STOCK"

    def test_stock_baixo(self):
        assert estado_item(quantidade=3, stock_minimo=5) == "STOCK_BAIXO"


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

    def test_saida_maior_que_stock_bloqueada(self, api_client, nurse_user, med_urg):
        api_client.force_authenticate(user=nurse_user)
        r = api_client.post(
            f"/api/v1/stock/items/{med_urg.pk}/saida/",
            {"quantidade": 999},
            format="json",
        )
        assert r.status_code == 400
        med_urg.refresh_from_db()
        assert med_urg.quantidade_stock == 10

    def test_create_item_com_stock_inicial(self, api_client, nurse_user):
        api_client.force_authenticate(user=nurse_user)
        r = api_client.post(
            "/api/v1/stock/items/",
            {
                "nome": "Seringa 5ml",
                "categoria": "MATERIAL_CLINICO",
                "unidade": "unidade",
                "quantidade_inicial": 15,
                "stock_minimo": 5,
            },
            format="json",
        )
        assert r.status_code == 201
        item = MedicamentoUrgencia.objects.get(nome="Seringa 5ml")
        assert item.quantidade_stock == 15
        assert MovimentoStockUrgencia.objects.filter(medicamento=item, tipo="ENTRADA").exists()

    def test_rececao_nao_altera(self, api_client, receptionist_user, med_urg):
        api_client.force_authenticate(user=receptionist_user)
        r = api_client.post(
            f"/api/v1/stock/items/{med_urg.pk}/saida/",
            {"quantidade": 1},
            format="json",
        )
        assert r.status_code == 403

    def test_medico_read_only(self, api_client, doctor_user, med_urg):
        api_client.force_authenticate(user=doctor_user)
        listed = api_client.get("/api/v1/stock/items/")
        assert listed.status_code == 200
        r = api_client.post(
            f"/api/v1/stock/items/{med_urg.pk}/entrada/",
            {"quantidade": 1},
            format="json",
        )
        assert r.status_code == 403

    def test_director_view(self, api_client, director_user, med_urg):
        api_client.force_authenticate(user=director_user)
        r = api_client.get("/api/v1/stock/dashboard/")
        assert r.status_code == 200
        assert "total_itens" in r.data["data"]

    def test_patch_nao_edita_quantidade(self, api_client, nurse_user, med_urg):
        api_client.force_authenticate(user=nurse_user)
        api_client.patch(
            f"/api/v1/stock/items/{med_urg.pk}/",
            {"quantidade_stock": 99, "stock_minimo": 4},
            format="json",
        )
        med_urg.refresh_from_db()
        assert med_urg.quantidade_stock == 10
        assert med_urg.stock_minimo == 4

    def test_movements_sem_delete(self, api_client, nurse_user, med_urg):
        api_client.force_authenticate(user=nurse_user)
        api_client.post(
            f"/api/v1/stock/items/{med_urg.pk}/entrada/",
            {"quantidade": 1},
            format="json",
        )
        mov = MovimentoStockUrgencia.objects.first()
        r = api_client.delete(f"/api/v1/stock/movements/{mov.pk}/")
        assert r.status_code in (403, 404, 405)


@pytest.mark.django_db
class TestImportStock:
    def test_cx50_nao_e_quantidade(self, tmp_path, nurse_user):
        path = tmp_path / "stock.csv"
        path.write_text(
            "nome_actual,tipo,unidade,quantidade_actual,stock_minimo,manter_no_stock,quantidade_texto_original\n"
            "Compressa,MATERIAL_CLINICO,caixa,,5,SIM,CX/50\n"
            "Ceftriaxona,MEDICAMENTO,frasco,8,5,SIM,\n"
            "Cartao,DOCUMENTO_CARTAO,un,3,1,NAO,\n",
            encoding="utf-8",
        )
        call_command("import_stock_urgencia", dry_run=True, file=str(path), actor_email=nurse_user.email)
        assert MedicamentoUrgencia.objects.count() == 0
        call_command("import_stock_urgencia", apply=True, file=str(path), actor_email=nurse_user.email)
        cef = MedicamentoUrgencia.objects.get(nome="Ceftriaxona")
        assert cef.quantidade_stock == 8
        mov = MovimentoStockUrgencia.objects.get(medicamento=cef)
        assert mov.tipo == "ENTRADA"
        assert mov.origem == "STOCK_INICIAL_CLINICA"
        assert mov.quantidade_antes == 0
        assert mov.quantidade_depois == 8
        assert not MedicamentoUrgencia.objects.filter(nome="Compressa").exists()
        assert not MedicamentoUrgencia.objects.filter(nome="Cartao").exists()
        call_command("import_stock_urgencia", apply=True, file=str(path), actor_email=nurse_user.email)
        assert MedicamentoUrgencia.objects.filter(nome="Ceftriaxona").count() == 1

    def test_plan_classifies_unconfirmed_and_empty_qty(self, tmp_path):
        path = tmp_path / "ficha.csv"
        path.write_text(
            "nome,tipo,unidade,quantidade_actual,stock_minimo,manter_no_stock\n"
            "Adrenalina,MEDICAMENTO,ampola,,5,\n"
            "Seringa,MATERIAL_CLINICO,,4,2,SIM\n"
            "Luvas,MATERIAL_CLINICO,caixa,CX/50,2,SIM\n"
            "Oxitocina,MEDICAMENTO,ampola,6,2,SIM\n",
            encoding="utf-8",
        )
        plan = build_import_plan(path)
        statuses = {item["nome"]: item["status"] for item in plan["itens"]}
        assert statuses["Adrenalina"] == NAO_MANTER
        assert statuses["Seringa"] == UNIDADE_AUSENTE
        assert statuses["Luvas"] == QUANTIDADE_INVALIDA
        assert statuses["Oxitocina"] == VALIDO
        assert plan["a_criar"] == 1

    def test_apply_blocked_when_nothing_valid(self, tmp_path, nurse_user):
        path = tmp_path / "vazio.csv"
        path.write_text(
            "nome,tipo,unidade,quantidade_actual,manter_no_stock\n"
            "Ceftriaxona,MEDICAMENTO,frasco,,\n",
            encoding="utf-8",
        )
        with pytest.raises(CommandError):
            call_command("import_stock_urgencia", apply=True, file=str(path), actor_email=nurse_user.email)
        assert MedicamentoUrgencia.objects.count() == 0

    def test_uat_entrada_saida_bloqueio(self, med_urg, nurse_user):
        StockUrgenciaService.registar_movimento(
            med_urg, tipo="ENTRADA", quantidade=5, operador=nurse_user
        )
        med_urg.refresh_from_db()
        assert med_urg.quantidade_stock == 15
        StockUrgenciaService.registar_movimento(
            med_urg, tipo="SAIDA", quantidade=2, operador=nurse_user
        )
        med_urg.refresh_from_db()
        assert med_urg.quantidade_stock == 13
        with pytest.raises(StockUrgenciaError):
            StockUrgenciaService.registar_movimento(
                med_urg, tipo="SAIDA", quantidade=50, operador=nurse_user
            )
        StockUrgenciaService.registar_movimento(
            med_urg, tipo="AJUSTE", quantidade=5, operador=nurse_user
        )
        med_urg.refresh_from_db()
        assert med_urg.quantidade_stock == 5
        StockUrgenciaService.registar_movimento(
            med_urg, tipo="PERDA_EXPIRACAO", quantidade=5, operador=nurse_user
        )
        med_urg.refresh_from_db()
        assert med_urg.quantidade_stock == 0
        assert med_urg.estado == "SEM_STOCK"
