"""Testes Sprint 17 — preços confirmados, faturação e alinhamento lab."""

from decimal import Decimal
from io import StringIO

import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from rest_framework import status

from apps.authentication.models import UserRole
from apps.billing.models import Servico, ServicoPrecoHistorico
from apps.billing.services.billing_service import BillingService
from apps.billing.services.catalog_service import MSG_PRECO_NAO_CONFIRMADO
from apps.settings.models import Departamento, MedicoPerfil, TipoExameLaboratorio

User = get_user_model()


@pytest.mark.django_db
class TestPrecoConfirmadoImport:
    def test_import_ignora_linha_vazia(self, db, seed_rbac, admin_user):
        Departamento.objects.create(codigo="LAB", nome="Lab")
        servico = Servico.objects.create(
            codigo="S-VAL", nome="Teste", categoria="LABORATORIO", preco=0, preco_confirmado=False
        )
        from pathlib import Path

        import tempfile

        csv = (
            "codigo,nome,categoria,departamento,preco_actual_fcfa,preco_confirmado_fcfa,"
            "confirmado_por,data_confirmacao,observacoes\n"
            "S-VAL,Teste,Laboratório,LAB,,,,\n"
            "S-VAL,Teste,Laboratório,LAB,,15000,Admin,2026-07-31,ok\n"
        )
        with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, encoding="utf-8") as f:
            f.write(csv)
            path = f.name
        call_command(
            "import_catalogo_sauvida",
            f"--file={path}",
            "--apply",
            "--update-existing",
            f"--actor-email={admin_user.email}",
        )
        servico = Servico.objects.get(codigo="S-VAL")
        assert servico.preco == Decimal("15000")
        assert servico.preco_confirmado is True
        assert ServicoPrecoHistorico.objects.filter(servico=servico).exists()

    def test_preco_negativo_rejeitado(self, db, seed_rbac, tmp_path):
        Departamento.objects.create(codigo="LAB", nome="Lab")
        Servico.objects.create(codigo="S-NEG", nome="N", categoria="CONSULTA", preco=0)
        path = tmp_path / "v.csv"
        path.write_text(
            "codigo,nome,categoria,departamento,preco_actual_fcfa,preco_confirmado_fcfa,"
            "confirmado_por,data_confirmacao,observacoes\n"
            "S-NEG,N,Consulta,LAB,,-100,,,\n",
            encoding="utf-8",
        )
        out = StringIO()
        with pytest.raises(CommandError):
            call_command(
                "import_catalogo_sauvida",
                f"--file={path}",
                "--apply",
                stdout=out,
            )


@pytest.mark.django_db
class TestFaturacaoPrecoConfirmado:
    def test_rececao_nao_fatura_sem_preco_confirmado(self, receptionist_user, patient_for_billing, seed_rbac):
        servico = Servico.objects.create(
            codigo="PEND-1",
            nome="Pendente",
            categoria="CONSULTA",
            preco=Decimal("1000"),
            preco_confirmado=False,
        )
        with pytest.raises(ValueError, match=MSG_PRECO_NAO_CONFIRMADO[:20]):
            BillingService.gerar_fatura(
                receptionist_user,
                paciente_id=patient_for_billing.pk,
                itens=[{"servico_id": servico.pk, "quantidade": 1}],
            )

    def test_admin_pode_faturar_pendente(self, admin_user, patient_for_billing, seed_rbac):
        servico = Servico.objects.create(
            codigo="PEND-ADM",
            nome="Pendente",
            categoria="CONSULTA",
            preco=Decimal("1000"),
            preco_confirmado=False,
        )
        fatura = BillingService.gerar_fatura(
            admin_user,
            paciente_id=patient_for_billing.pk,
            itens=[{"servico_id": servico.pk, "quantidade": 1}],
        )
        assert fatura.itens.count() == 1


@pytest.mark.django_db
class TestMedicoPerfil:
    def test_medico_duplicado(self, api_client, admin_user, seed_rbac):
        medico = User.objects.create_user(
            email="m1@test.gw", password="Med@12345", first_name="M", last_name="D", role=UserRole.MEDICO
        )
        MedicoPerfil.objects.create(utilizador=medico)
        api_client.force_authenticate(user=admin_user)
        response = api_client.post(
            "/api/v1/settings/medico-perfis/",
            {"utilizador": medico.pk, "activo": True, "disponivel_marcacao": True},
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestAlignLab:
    def test_align_dry_run(self, db, seed_rbac):
        dept = Departamento.objects.create(codigo="LAB", nome="Lab")
        servico = Servico.objects.create(
            codigo="LAB-HEMO", nome="Hemograma", categoria="LABORATORIO", departamento=dept, preco_confirmado=True, preco=100
        )
        TipoExameLaboratorio.objects.create(codigo="LAB-HEMO-TIPO", nome="Hemograma", categoria="Hematologia")
        out = StringIO()
        call_command("align_lab_services", "--dry-run", stdout=out)
        assert "DRY-RUN" in out.getvalue()


@pytest.mark.django_db
class TestPermissoesPreco:
    def test_director_nao_altera_preco(self, api_client, director_user, seed_rbac):
        servico = Servico.objects.create(
            codigo="DIR-P",
            nome="Teste",
            categoria="CONSULTA",
            preco=Decimal("1000"),
            preco_confirmado=True,
        )
        api_client.force_authenticate(user=director_user)
        response = api_client.patch(
            f"/api/v1/billing/services/{servico.pk}/",
            {"preco": "2000"},
            format="json",
        )
        assert response.status_code in (
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_403_FORBIDDEN,
        )

    def test_rececionista_nao_altera_preco(self, api_client, receptionist_user, seed_rbac):
        servico = Servico.objects.create(
            codigo="REC-P",
            nome="Teste",
            categoria="CONSULTA",
            preco=Decimal("1000"),
            preco_confirmado=True,
        )
        api_client.force_authenticate(user=receptionist_user)
        response = api_client.patch(
            f"/api/v1/billing/services/{servico.pk}/",
            {"preco": "2000"},
            format="json",
        )
        assert response.status_code in (
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_403_FORBIDDEN,
        )


@pytest.fixture
def director_user(db):
    from apps.authentication.models import UserRole

    return User.objects.create_user(
        email="director@s17.test",
        password="Dir@12345",
        first_name="Dir",
        last_name="Test",
        role=UserRole.DIRECTOR,
    )


@pytest.fixture
def patient_for_billing(db, receptionist_user):
    from apps.patients.services.patient_service import PatientService

    return PatientService.create(
        {
            "first_name": "S17",
            "last_name": "Paciente",
            "birth_date": __import__("datetime").date(1992, 2, 2),
            "gender": "M",
            "phone": "+245955000777",
            "document_number": "S17001",
            "document_type": "BI",
        },
        user=receptionist_user,
    )
