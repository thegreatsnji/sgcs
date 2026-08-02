"""Testes Sprint 18 — validação, importação e preservação de faturas."""

from decimal import Decimal

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from apps.billing.models import Fatura, Servico, ServicoPrecoHistorico
from apps.billing.services.billing_service import BillingService
from apps.billing.services.catalog_service import confirmar_preco_servico
from apps.billing.services.preco_validation_service import validar_ficheiro_precos


@pytest.mark.django_db
class TestValidacaoPrecosCsv:
    def test_todas_pendentes_sem_preco(self, tmp_path):
        cat = tmp_path / "cat.csv"
        cat.write_text(
            "codigo,nome,categoria,departamento,especialidade,preco_fcfa,ativo\n"
            "CONS-CLIN-GER,Consulta de Clínica Geral,CONSULTA,CONS-GER,,0,1\n",
            encoding="utf-8",
        )
        src = tmp_path / "v.csv"
        src.write_text(
            "codigo,nome,categoria,departamento,preco_actual_fcfa,preco_confirmado_fcfa,"
            "confirmado_por,data_confirmacao,observacoes\n"
            "CONS-CLIN-GER,Consulta,Consulta,CONS-GER,,,,,\n",
            encoding="utf-8",
        )
        rel = validar_ficheiro_precos(src, catalog_path=cat)
        assert rel.pendentes == 1
        assert rel.validas == 0
        assert not rel.bloqueia_importacao

    def test_linha_valida_requer_metadados(self, tmp_path):
        cat = tmp_path / "catalogo_servicos_sauvida.csv"
        cat.write_text(
            "codigo,nome,categoria,departamento,especialidade,preco_fcfa,ativo\n"
            "S1,Serv,CONSULTA,CONS-GER,,0,1\n",
            encoding="utf-8",
        )
        src = tmp_path / "v.csv"
        src.write_text(
            "codigo,nome,categoria,departamento,preco_actual_fcfa,preco_confirmado_fcfa,"
            "confirmado_por,data_confirmacao,observacoes\n"
            "S1,Serv,Consulta,CONS-GER,,5000,Admin,2026-07-31,ok\n",
            encoding="utf-8",
        )
        rel = validar_ficheiro_precos(src, catalog_path=cat)
        assert rel.validas == 1

    def test_codigo_desconhecido_bloqueia(self, tmp_path):
        cat = tmp_path / "catalogo_servicos_sauvida.csv"
        cat.write_text("codigo,nome,categoria,departamento,especialidade,preco_fcfa,ativo\n", encoding="utf-8")
        src = tmp_path / "v.csv"
        src.write_text(
            "codigo,nome,categoria,departamento,preco_actual_fcfa,preco_confirmado_fcfa,"
            "confirmado_por,data_confirmacao,observacoes\n"
            "UNKNOWN,X,Consulta,CONS-GER,,1000,A,2026-07-31,\n",
            encoding="utf-8",
        )
        rel = validar_ficheiro_precos(src, catalog_path=cat)
        assert rel.bloqueia_importacao


@pytest.mark.django_db
class TestPreservacaoFatura:
    def test_alterar_preco_servico_nao_altera_item_emitido(
        self, admin_user, patient_for_billing, seed_rbac
    ):
        servico = Servico.objects.create(
            codigo="PRES-1",
            nome="Preservação",
            categoria="CONSULTA",
            preco=Decimal("1000"),
            preco_confirmado=True,
        )
        fatura = BillingService.gerar_fatura(
            admin_user,
            paciente_id=patient_for_billing.pk,
            itens=[{"servico_id": servico.pk, "quantidade": 1}],
        )
        item = fatura.itens.first()
        preco_item = item.preco

        confirmar_preco_servico(servico, Decimal("9999"), user=admin_user, origem="IMPORTACAO_VALIDADA")
        servico.refresh_from_db()
        item.refresh_from_db()

        assert servico.preco == Decimal("9999")
        assert item.preco == preco_item
        assert ServicoPrecoHistorico.objects.filter(servico=servico).exists()


@pytest.mark.django_db
class TestImportPrecoPendente:
    def test_apply_nao_confirma_sem_preco(self, admin_user, seed_rbac, tmp_path):
        Servico.objects.create(codigo="PEND-X", nome="P", categoria="CONSULTA", preco=0)
        path = tmp_path / "p.csv"
        path.write_text(
            "codigo,nome,categoria,departamento,preco_actual_fcfa,preco_confirmado_fcfa,"
            "confirmado_por,data_confirmacao,observacoes\n"
            "PEND-X,P,Consulta,CONS-GER,,,,,\n",
            encoding="utf-8",
        )
        call_command("import_catalogo_sauvida", f"--file={path}", "--apply", f"--actor-email={admin_user.email}")
        servico = Servico.objects.get(codigo="PEND-X")
        assert servico.preco_confirmado is False

    def test_preco_negativo_falha(self, admin_user, seed_rbac, tmp_path):
        Servico.objects.create(codigo="NEG-1", nome="N", categoria="CONSULTA", preco=0)
        path = tmp_path / "n.csv"
        path.write_text(
            "codigo,nome,categoria,departamento,preco_actual_fcfa,preco_confirmado_fcfa,"
            "confirmado_por,data_confirmacao,observacoes\n"
            "NEG-1,N,Consulta,CONS-GER,,-50,A,2026-07-31,\n",
            encoding="utf-8",
        )
        with pytest.raises(CommandError):
            call_command(
                "import_catalogo_sauvida",
                f"--file={path}",
                "--apply",
                f"--actor-email={admin_user.email}",
            )


@pytest.fixture
def patient_for_billing(db, receptionist_user):
    from apps.patients.services.patient_service import PatientService

    return PatientService.create(
        {
            "first_name": "S18",
            "last_name": "Paciente",
            "birth_date": __import__("datetime").date(1993, 3, 3),
            "gender": "M",
            "phone": "+245955000888",
            "document_number": "S18001",
            "document_type": "BI",
        },
        user=receptionist_user,
    )
