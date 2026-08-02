"""Testes Sprint 18.1 — redução de valores, catálogo real e alinhamento lab."""

from decimal import Decimal
from pathlib import Path

import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command
from rest_framework import status

from apps.audit_logs.models import AuditAction, AuditLog
from apps.authentication.models import UserRole
from apps.billing.constants import EstadoAutorizacaoReducao, MotivoReducao
from apps.billing.models import ItemFatura, ReducaoValorAutorizacao, Servico
from apps.billing.services.billing_service import BillingService
from apps.billing.services.reduction_service import ReductionError, resolve_item_pricing
from apps.settings.models import ConfiguracaoFaturacao

User = get_user_model()


@pytest.fixture
def director_user(db, seed_rbac):
    return User.objects.create_user(
        email="director.reducao@test.local",
        password="TestPass123!",
        first_name="Director",
        last_name="Teste",
        role=UserRole.DIRECTOR,
        is_active=True,
    )


DATA = Path(__file__).resolve().parents[3] / "data"


@pytest.fixture
def patient_for_billing(db, receptionist_user):
    from apps.patients.services.patient_service import PatientService

    return PatientService.create(
        {
            "first_name": "S181",
            "last_name": "Paciente",
            "birth_date": __import__("datetime").date(1992, 2, 2),
            "gender": "M",
            "phone": "+245955000888",
            "document_number": "S181001",
            "document_type": "BI",
        },
        user=receptionist_user,
    )


@pytest.fixture
def billing_config(db):
    from apps.settings.services.settings_service import SettingsService

    cfg = SettingsService._get_singleton(ConfiguracaoFaturacao)
    cfg.permitir_reducao_rececao = True
    cfg.limite_reducao_rececao_percentual = Decimal("15")
    cfg.exigir_motivo_reducao = True
    cfg.exigir_autorizacao_acima_limite = True
    cfg.permitir_valor_zero = False
    cfg.save()
    return cfg


@pytest.mark.django_db
class TestReducaoValores:
    def test_preco_oficial_preservado_no_item(
        self, receptionist_user, patient_for_billing, seed_rbac, billing_config
    ):
        servico = Servico.objects.create(
            codigo="RED-1",
            nome="Consulta teste",
            categoria="CONSULTA",
            preco=Decimal("10000"),
            preco_confirmado=True,
        )
        fatura = BillingService.gerar_fatura(
            receptionist_user,
            paciente_id=patient_for_billing.pk,
            itens=[
                {
                    "servico_id": servico.pk,
                    "quantidade": 1,
                    "preco_cobrado": "9000",
                    "motivo_reducao": MotivoReducao.DIFICULDADE_FINANCEIRA,
                }
            ],
        )
        item = fatura.itens.get()
        assert item.preco == Decimal("9000")
        assert item.preco_oficial == Decimal("10000")
        assert servico.preco == Decimal("10000")
        assert item.valor_reducao == Decimal("1000")

    def test_valor_superior_oficial_bloqueado(
        self, receptionist_user, seed_rbac, billing_config
    ):
        servico = Servico.objects.create(
            codigo="RED-2",
            nome="S",
            categoria="CONSULTA",
            preco=Decimal("5000"),
            preco_confirmado=True,
        )
        with pytest.raises(ReductionError):
            resolve_item_pricing(
                servico,
                receptionist_user,
                quantidade=1,
                preco_cobrado_raw="6000",
                motivo_reducao=MotivoReducao.OUTRO,
                observacao_reducao="teste",
            )

    def test_motivo_obrigatorio(self, receptionist_user, seed_rbac, billing_config):
        servico = Servico.objects.create(
            codigo="RED-3",
            nome="S",
            categoria="CONSULTA",
            preco=Decimal("5000"),
            preco_confirmado=True,
        )
        with pytest.raises(ReductionError):
            resolve_item_pricing(
                servico,
                receptionist_user,
                quantidade=1,
                preco_cobrado_raw="4500",
            )

    def test_outro_exige_observacao(self, receptionist_user, seed_rbac, billing_config):
        servico = Servico.objects.create(
            codigo="RED-4",
            nome="S",
            categoria="CONSULTA",
            preco=Decimal("5000"),
            preco_confirmado=True,
        )
        with pytest.raises(ReductionError):
            resolve_item_pricing(
                servico,
                receptionist_user,
                quantidade=1,
                preco_cobrado_raw="4500",
                motivo_reducao=MotivoReducao.OUTRO,
            )

    def test_acima_limite_exige_autorizacao(
        self, receptionist_user, patient_for_billing, seed_rbac, billing_config
    ):
        servico = Servico.objects.create(
            codigo="RED-5",
            nome="S",
            categoria="CONSULTA",
            preco=Decimal("10000"),
            preco_confirmado=True,
        )
        with pytest.raises(ValueError, match="autoriza"):
            BillingService.gerar_fatura(
                receptionist_user,
                paciente_id=patient_for_billing.pk,
                itens=[
                    {
                        "servico_id": servico.pk,
                        "quantidade": 1,
                        "preco_cobrado": "5000",
                        "motivo_reducao": MotivoReducao.APOIO_SOCIAL,
                    }
                ],
            )

    def test_aprovacao_director_permite_fatura(
        self,
        receptionist_user,
        director_user,
        patient_for_billing,
        seed_rbac,
        billing_config,
    ):
        servico = Servico.objects.create(
            codigo="RED-6",
            nome="S",
            categoria="CONSULTA",
            preco=Decimal("10000"),
            preco_confirmado=True,
        )
        from apps.billing.services.reduction_service import (
            decidir_autorizacao_reducao,
            solicitar_autorizacao_reducao,
        )

        auth = solicitar_autorizacao_reducao(
            receptionist_user,
            servico_id=servico.pk,
            paciente_id=patient_for_billing.pk,
            quantidade=1,
            preco_proposto=Decimal("5000"),
            motivo_reducao=MotivoReducao.DIFICULDADE_FINANCEIRA,
        )
        decidir_autorizacao_reducao(auth.pk, director_user, aprovar=True)
        fatura = BillingService.gerar_fatura(
            receptionist_user,
            paciente_id=patient_for_billing.pk,
            itens=[
                {
                    "servico_id": servico.pk,
                    "quantidade": 1,
                    "preco_cobrado": "5000",
                    "motivo_reducao": MotivoReducao.DIFICULDADE_FINANCEIRA,
                    "autorizacao_reducao_id": auth.pk,
                }
            ],
        )
        item = fatura.itens.get()
        assert item.estado_autorizacao_reducao == EstadoAutorizacaoReducao.APROVADA

    def test_auditoria_reducao(
        self, receptionist_user, patient_for_billing, seed_rbac, billing_config
    ):
        servico = Servico.objects.create(
            codigo="RED-7",
            nome="S",
            categoria="CONSULTA",
            preco=Decimal("10000"),
            preco_confirmado=True,
        )
        BillingService.gerar_fatura(
            receptionist_user,
            paciente_id=patient_for_billing.pk,
            itens=[
                {
                    "servico_id": servico.pk,
                    "quantidade": 1,
                    "preco_cobrado": "9000",
                    "motivo_reducao": MotivoReducao.CORTESIA,
                }
            ],
        )
        assert AuditLog.objects.filter(action=AuditAction.REDUCAO_VALOR_APLICADA).exists()

    def test_alterar_servico_nao_altera_item_antigo(
        self, receptionist_user, patient_for_billing, seed_rbac, billing_config
    ):
        servico = Servico.objects.create(
            codigo="RED-8",
            nome="S",
            categoria="CONSULTA",
            preco=Decimal("8000"),
            preco_confirmado=True,
        )
        fatura = BillingService.gerar_fatura(
            receptionist_user,
            paciente_id=patient_for_billing.pk,
            itens=[{"servico_id": servico.pk, "quantidade": 1}],
        )
        item_id = fatura.itens.get().pk
        servico.preco = Decimal("12000")
        servico.save()
        item = ItemFatura.objects.get(pk=item_id)
        assert item.preco_oficial == Decimal("8000")


@pytest.mark.django_db
class TestCatalogoRealValidacao:
    def test_csv_validacao_existe(self):
        path = DATA / "catalogo_real_validacao_clinica.csv"
        assert path.is_file()
        text = path.read_text(encoding="utf-8")
        assert "LAB-LINHA-SEM-NOME" in text
        assert "REVISAR" not in text or "tipo_pendencia" in text

    def test_duplicados_nao_resolvidos_automaticamente(self):
        import json

        dup = json.loads((DATA / "catalogo_real_duplicados.json").read_text(encoding="utf-8"))
        assert len(dup) == 6


@pytest.mark.django_db
class TestReducaoAPI:
    def test_listar_pendentes_director(self, api_client, director_user, seed_rbac, billing_config):
        servico = Servico.objects.create(
            codigo="API-R1",
            nome="S",
            categoria="CONSULTA",
            preco=Decimal("10000"),
            preco_confirmado=True,
        )
        ReducaoValorAutorizacao.objects.create(
            servico=servico,
            solicitado_por=director_user,
            motivo_reducao=MotivoReducao.APOIO_SOCIAL,
            preco_oficial=Decimal("10000"),
            preco_proposto=Decimal("7000"),
            diferenca_unitaria=Decimal("3000"),
            percentual_reducao=Decimal("30"),
            estado=EstadoAutorizacaoReducao.PENDENTE,
        )
        api_client.force_authenticate(user=director_user)
        r = api_client.get("/api/v1/billing/reducoes/?estado=PENDENTE")
        assert r.status_code == status.HTTP_200_OK
