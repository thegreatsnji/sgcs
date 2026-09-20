"""Testes do resumo financeiro operacional da Receção (Sprint 23.1)."""

from datetime import timedelta
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status

from apps.authentication.models import UserRole
from apps.billing.constants import MetodoPagamento, MotivoReducao, PagamentoEstado
from apps.billing.models import Servico
from apps.billing.period import resolve_periodo
from apps.billing.services.billing_service import BillingService
from apps.billing.services.resumo_operacional import get_resumo_operacional
from apps.patients.models import PatientHistory
from apps.patients.constants import HistoryEventType
from apps.patients.services.history_service import PatientHistoryService
from apps.settings.models import ConfiguracaoFaturacao

User = get_user_model()


@pytest.fixture
def patient_for_billing(db, receptionist_user):
    from apps.patients.services.patient_service import PatientService

    return PatientService.create(
        {
            "first_name": "Resumo",
            "last_name": "Operacional",
            "birth_date": __import__("datetime").date(1990, 1, 10),
            "gender": "F",
            "phone": "+245955111000",
            "document_number": "RESUMO001",
            "document_type": "BI",
        },
        user=receptionist_user,
    )


@pytest.fixture
def servico_consulta(db):
    return Servico.objects.create(
        codigo="RES-CONS",
        nome="Consulta resumo",
        categoria="CONSULTA",
        preco=Decimal("10000.00"),
        preco_confirmado=True,
    )


@pytest.fixture
def billing_config(db):
    from apps.settings.services.settings_service import SettingsService

    cfg = SettingsService._get_singleton(ConfiguracaoFaturacao)
    cfg.permitir_reducao_rececao = True
    cfg.limite_reducao_rececao_percentual = Decimal("50")
    cfg.exigir_motivo_reducao = True
    cfg.exigir_autorizacao_acima_limite = False
    cfg.permitir_valor_zero = False
    cfg.save()
    return cfg


def _emitir_e_pagar(user, patient, servico, *, valor_pago=None, itens=None):
    fatura = BillingService.gerar_fatura(
        user,
        paciente_id=patient.pk,
        itens=itens
        or [{"servico_id": servico.pk, "quantidade": 1}],
    )
    pagar = Decimal(valor_pago) if valor_pago is not None else fatura.total
    pag = BillingService.registar_pagamento(
        fatura.pk,
        user,
        valor=pagar,
        metodo_pagamento=MetodoPagamento.DINHEIRO,
    )
    BillingService.confirmar_pagamento(pag.pk, user)
    fatura.refresh_from_db()
    pag.refresh_from_db()
    return fatura, pag


@pytest.mark.django_db
class TestResumoOperacionalService:
    def test_periodo_vazio_zero(self):
        hoje = timezone.localdate()
        data = get_resumo_operacional(data_inicio=hoje, data_fim=hoje)
        assert data["total_faturado"] == "0.00"
        assert data["total_recebido"] == "0.00"
        assert data["saldo_pendente"] == "0.00"
        assert data["total_reducoes"] == "0.00"
        assert data["numero_pagamentos"] == 0

    def test_total_hoje(
        self, receptionist_user, patient_for_billing, servico_consulta
    ):
        fatura, _ = _emitir_e_pagar(
            receptionist_user, patient_for_billing, servico_consulta
        )
        hoje = timezone.localdate()
        data = get_resumo_operacional(data_inicio=hoje, data_fim=hoje)
        assert Decimal(data["total_faturado"]) == fatura.total
        assert Decimal(data["total_recebido"]) == fatura.total
        assert data["saldo_pendente"] == "0.00"
        assert data["numero_pagamentos"] == 1

    def test_semana_e_mes_incluem_hoje(
        self, receptionist_user, patient_for_billing, servico_consulta
    ):
        _emitir_e_pagar(receptionist_user, patient_for_billing, servico_consulta)
        inicio_s, fim_s = resolve_periodo("semana")
        inicio_m, fim_m = resolve_periodo("mes")
        semana = get_resumo_operacional(data_inicio=inicio_s, data_fim=fim_s)
        mes = get_resumo_operacional(data_inicio=inicio_m, data_fim=fim_m)
        assert Decimal(semana["total_recebido"]) > 0
        assert Decimal(mes["total_recebido"]) > 0

    def test_intervalo_personalizado_inclusivo(
        self, receptionist_user, patient_for_billing, servico_consulta
    ):
        fatura, _ = _emitir_e_pagar(
            receptionist_user, patient_for_billing, servico_consulta
        )
        hoje = timezone.localdate()
        data = get_resumo_operacional(data_inicio=hoje, data_fim=hoje)
        assert Decimal(data["total_faturado"]) == fatura.total
        # Dia anterior: zero
        ontem = hoje - timedelta(days=1)
        vazio = get_resumo_operacional(data_inicio=ontem, data_fim=ontem)
        assert vazio["total_faturado"] == "0.00"
        assert vazio["total_recebido"] == "0.00"

    def test_pagamento_data_diferente_da_fatura(
        self, receptionist_user, patient_for_billing, servico_consulta
    ):
        fatura = BillingService.gerar_fatura(
            receptionist_user,
            paciente_id=patient_for_billing.pk,
            itens=[{"servico_id": servico_consulta.pk, "quantidade": 1}],
        )
        # Retrocede emissão para ontem
        ontem = timezone.now() - timedelta(days=1)
        fatura.emitida_em = ontem
        fatura.save(update_fields=["emitida_em"])

        pag = BillingService.registar_pagamento(
            fatura.pk,
            receptionist_user,
            valor=fatura.total,
            metodo_pagamento=MetodoPagamento.DINHEIRO,
        )
        BillingService.confirmar_pagamento(pag.pk, receptionist_user)

        hoje = timezone.localdate()
        dia_ontem = (timezone.localtime(ontem)).date()

        res_ontem = get_resumo_operacional(data_inicio=dia_ontem, data_fim=dia_ontem)
        res_hoje = get_resumo_operacional(data_inicio=hoje, data_fim=hoje)

        assert Decimal(res_ontem["total_faturado"]) == fatura.total
        assert res_ontem["total_recebido"] == "0.00"
        # Saldo = ainda por receber *agora* nas faturas do período (já liquidada hoje → 0)
        assert res_ontem["saldo_pendente"] == "0.00"

        assert res_hoje["total_faturado"] == "0.00"
        assert Decimal(res_hoje["total_recebido"]) == fatura.total
        assert res_hoje["numero_pagamentos"] == 1
        assert res_hoje["saldo_pendente"] == "0.00"

    def test_pagamento_parcial(
        self, receptionist_user, patient_for_billing, servico_consulta
    ):
        fatura, _ = _emitir_e_pagar(
            receptionist_user,
            patient_for_billing,
            servico_consulta,
            valor_pago=Decimal("6000.00"),
        )
        hoje = timezone.localdate()
        data = get_resumo_operacional(data_inicio=hoje, data_fim=hoje)
        assert Decimal(data["total_faturado"]) == fatura.total
        assert Decimal(data["total_recebido"]) == Decimal("6000.00")
        assert Decimal(data["saldo_pendente"]) == fatura.total - Decimal("6000.00")
        assert data["total_reducoes"] == "0.00"

    def test_reducao(
        self, receptionist_user, patient_for_billing, servico_consulta, billing_config
    ):
        fatura, _ = _emitir_e_pagar(
            receptionist_user,
            patient_for_billing,
            servico_consulta,
            itens=[
                {
                    "servico_id": servico_consulta.pk,
                    "quantidade": 1,
                    "preco_cobrado": "8000",
                    "motivo_reducao": MotivoReducao.DIFICULDADE_FINANCEIRA,
                }
            ],
        )
        hoje = timezone.localdate()
        data = get_resumo_operacional(data_inicio=hoje, data_fim=hoje)
        assert Decimal(data["total_faturado"]) == fatura.total
        assert Decimal(data["total_recebido"]) == fatura.total
        assert data["saldo_pendente"] == "0.00"
        assert Decimal(data["total_reducoes"]) == Decimal("2000.00")

    def test_multiplos_pagamentos_mesma_fatura(
        self, receptionist_user, patient_for_billing, servico_consulta
    ):
        fatura = BillingService.gerar_fatura(
            receptionist_user,
            paciente_id=patient_for_billing.pk,
            itens=[{"servico_id": servico_consulta.pk, "quantidade": 1}],
        )
        for valor in (Decimal("4000.00"), Decimal("6000.00")):
            pag = BillingService.registar_pagamento(
                fatura.pk,
                receptionist_user,
                valor=valor,
                metodo_pagamento=MetodoPagamento.DINHEIRO,
            )
            BillingService.confirmar_pagamento(pag.pk, receptionist_user)

        hoje = timezone.localdate()
        data = get_resumo_operacional(data_inicio=hoje, data_fim=hoje)
        assert data["numero_pagamentos"] == 2
        assert Decimal(data["total_recebido"]) == Decimal("10000.00")
        assert data["saldo_pendente"] == "0.00"

    def test_fatura_cancelada_excluida(
        self, receptionist_user, patient_for_billing, servico_consulta
    ):
        fatura = BillingService.gerar_fatura(
            receptionist_user,
            paciente_id=patient_for_billing.pk,
            itens=[{"servico_id": servico_consulta.pk, "quantidade": 1}],
        )
        BillingService.cancelar_fatura(fatura.pk, receptionist_user)
        hoje = timezone.localdate()
        data = get_resumo_operacional(data_inicio=hoje, data_fim=hoje)
        assert data["total_faturado"] == "0.00"
        assert data["saldo_pendente"] == "0.00"

    def test_pagamento_nao_confirmado_excluido(
        self, receptionist_user, patient_for_billing, servico_consulta
    ):
        fatura = BillingService.gerar_fatura(
            receptionist_user,
            paciente_id=patient_for_billing.pk,
            itens=[{"servico_id": servico_consulta.pk, "quantidade": 1}],
        )
        BillingService.registar_pagamento(
            fatura.pk,
            receptionist_user,
            valor=fatura.total,
            metodo_pagamento=MetodoPagamento.DINHEIRO,
        )
        hoje = timezone.localdate()
        data = get_resumo_operacional(data_inicio=hoje, data_fim=hoje)
        assert Decimal(data["total_faturado"]) == fatura.total
        assert data["total_recebido"] == "0.00"
        assert data["numero_pagamentos"] == 0
        assert Decimal(data["saldo_pendente"]) == fatura.total

    def test_pagamento_reembolsado_excluido(
        self, receptionist_user, patient_for_billing, servico_consulta
    ):
        fatura, pag = _emitir_e_pagar(
            receptionist_user, patient_for_billing, servico_consulta
        )
        pag.estado = PagamentoEstado.REEMBOLSADO
        pag.save(update_fields=["estado"])
        hoje = timezone.localdate()
        data = get_resumo_operacional(data_inicio=hoje, data_fim=hoje)
        assert data["total_recebido"] == "0.00"
        assert data["numero_pagamentos"] == 0
        # Fatura continua; saldo recalcula sem o pagamento reembolsado
        assert Decimal(data["saldo_pendente"]) == fatura.total

    def test_historico_migrado_excluido(
        self, receptionist_user, patient_for_billing
    ):
        """PatientHistory financeiro NÃO alimenta o resumo operacional."""
        PatientHistoryService.record(
            patient_for_billing,
            event_type=HistoryEventType.REGISTO,
            title="Pagamento histórico Excel",
            description="Não deve entrar na receita",
            event_date=timezone.now(),
            source_module="MIGRACAO_EXCEL_SAUVIDA",
            metadata={
                "source": "MIGRACAO_EXCEL_SAUVIDA",
                "preco_original": "50000",
                "desconto_original": "0",
                "valor_liquido_original": "50000",
            },
            user=receptionist_user,
        )
        assert PatientHistory.objects.filter(
            patient=patient_for_billing, source_module="MIGRACAO_EXCEL_SAUVIDA"
        ).exists()
        hoje = timezone.localdate()
        data = get_resumo_operacional(data_inicio=hoje, data_fim=hoje)
        assert data["total_faturado"] == "0.00"
        assert data["total_recebido"] == "0.00"
        assert data["total_reducoes"] == "0.00"


@pytest.mark.django_db
class TestResumoOperacionalAPI:
    def test_rececionista_autorizado(
        self, api_client, receptionist_user, patient_for_billing, servico_consulta
    ):
        _emitir_e_pagar(receptionist_user, patient_for_billing, servico_consulta)
        api_client.force_authenticate(user=receptionist_user)
        response = api_client.get(
            "/api/v1/billing/resumo-operacional/", {"periodo": "hoje"}
        )
        assert response.status_code == status.HTTP_200_OK
        body = response.data["data"]
        assert Decimal(body["total_recebido"]) > 0
        assert "total_faturado" in body
        assert "saldo_pendente" in body
        assert "total_reducoes" in body
        assert "numero_pagamentos" in body

    def test_periodos_query(
        self, api_client, receptionist_user, patient_for_billing, servico_consulta
    ):
        _emitir_e_pagar(receptionist_user, patient_for_billing, servico_consulta)
        api_client.force_authenticate(user=receptionist_user)
        for periodo in ("hoje", "semana", "mes"):
            response = api_client.get(
                "/api/v1/billing/resumo-operacional/", {"periodo": periodo}
            )
            assert response.status_code == status.HTTP_200_OK, periodo
            assert response.data["data"]["periodo"]["modo"] == periodo

        hoje = timezone.localdate()
        response = api_client.get(
            "/api/v1/billing/resumo-operacional/",
            {
                "periodo": "personalizado",
                "data_inicio": hoje.isoformat(),
                "data_fim": hoje.isoformat(),
            },
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["data"]["periodo"]["modo"] == "personalizado"

    def test_personalizado_sem_datas_400(self, api_client, receptionist_user):
        api_client.force_authenticate(user=receptionist_user)
        response = api_client.get(
            "/api/v1/billing/resumo-operacional/", {"periodo": "personalizado"}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_utilizador_sem_billing_view(self, api_client, db):
        user = User.objects.create_user(
            email="lab.resumo@test.gw",
            password="Lab@12345",
            first_name="Lab",
            last_name="SemBilling",
            role=UserRole.LABORATORIO,
        )
        api_client.force_authenticate(user=user)
        response = api_client.get(
            "/api/v1/billing/resumo-operacional/", {"periodo": "hoje"}
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_nao_autenticado(self, api_client):
        response = api_client.get(
            "/api/v1/billing/resumo-operacional/", {"periodo": "hoje"}
        )
        assert response.status_code in (
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
        )
