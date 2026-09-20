"""Sprint 23.4 — Integração E2E do perfil RECECIONISTA (UAT readiness)."""

from datetime import date, timedelta
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status

from apps.appointments.constants import AppointmentStatus
from apps.appointments.models import Appointment
from apps.appointments.services.appointment_service import AppointmentService
from apps.authentication.models import UserRole
from apps.billing.constants import CATALOGO_VERSAO_ATIVA, FaturaEstado, MotivoReducao
from apps.billing.models import Fatura, Pagamento, Recibo, Servico
from apps.billing.services.billing_service import BillingService
from apps.billing.services.resumo_operacional import get_resumo_operacional
from apps.patients.models import Patient, PatientAllergy
from apps.patients.services.patient_service import PatientService
from apps.reception.constants import QueueStatus
from apps.reception.models import ReceptionCheckIn, WaitingQueue
from apps.reception.services.reception_service import ReceptionService
from apps.settings.models import ConfiguracaoFaturacao
from apps.settings.services.settings_service import SettingsService

User = get_user_model()


@pytest.fixture
def doctor_user(db):
    return User.objects.create_user(
        email="medico.e2e@test.gw",
        password="Medico@123",
        first_name="Paulo",
        last_name="Médico",
        role=UserRole.MEDICO,
    )


@pytest.fixture
def servico_10k(db):
    return Servico.objects.create(
        codigo="E2E-CONS-10K",
        nome="Consulta E2E",
        categoria="CONSULTA",
        preco=Decimal("10000"),
        preco_confirmado=True,
        versao_catalogo=CATALOGO_VERSAO_ATIVA,
    )


def _patient(user, *, first="Utente", last="E2E", phone="+245955880001", doc="E2E-DOC-001"):
    return PatientService.create(
        {
            "first_name": first,
            "last_name": last,
            "birth_date": date(1991, 6, 12),
            "gender": "F",
            "phone": phone,
            "document_number": doc,
            "document_type": "BI",
            "address_street": "Bairro Central",
        },
        user=user,
        emergency_contacts=[
            {
                "name": "Contacto E2E",
                "phone": "+245955880099",
                "relationship": "CONJUGE",
                "is_primary": True,
            }
        ],
    )


def _pay_full(user, fatura, valor):
    p = BillingService.registar_pagamento(
        fatura.pk, user, valor=Decimal(valor), metodo_pagamento="DINHEIRO"
    )
    return BillingService.confirmar_pagamento(p.pk, user)


@pytest.mark.django_db
class TestE2EWalkInAndExisting:
    def test_walk_in_novo_sem_duplicados(
        self, api_client, receptionist_user, doctor_user, servico_10k
    ):
        api_client.force_authenticate(user=receptionist_user)
        search = api_client.get("/api/v1/patients/", {"search": "Walkin Novo"})
        assert search.status_code == 200
        assert search.data["data"]["count"] == 0

        create = api_client.post(
            "/api/v1/patients/",
            {
                "first_name": "Walkin",
                "last_name": "Novo",
                "birth_date": "12/06/1991",
                "gender": "F",
                "phone": "+245955881001",
                "document_type": "BI",
                "document_number": "E2E-WALK-001",
                "emergency_contacts": [
                    {
                        "name": "Contacto",
                        "phone": "+245955881002",
                        "relationship": "CONJUGE",
                        "is_primary": True,
                    }
                ],
            },
            format="json",
        )
        assert create.status_code == status.HTTP_201_CREATED
        patient_id = create.data["data"]["id"]
        assert Patient.objects.filter(document_number="E2E-WALK-001").count() == 1

        check_in = ReceptionService.check_in(patient_id, receptionist_user)
        entry = WaitingQueue.objects.get(check_in=check_in)
        assert WaitingQueue.objects.filter(patient_id=patient_id).count() == 1
        assert ReceptionCheckIn.objects.filter(patient_id=patient_id).count() == 1

        fatura = BillingService.gerar_fatura(
            receptionist_user,
            paciente_id=patient_id,
            itens=[{"servico_id": servico_10k.pk, "quantidade": 1}],
        )
        assert Fatura.objects.filter(paciente_id=patient_id).count() == 1
        _pay_full(receptionist_user, fatura, "10000")
        fatura.refresh_from_db()
        assert fatura.estado == FaturaEstado.PAGA
        assert Recibo.objects.filter(pagamento__fatura=fatura).count() == 1

        ReceptionService.assign_to_doctor(
            queue_id=entry.pk, user=receptionist_user, doctor_id=doctor_user.pk
        )
        assert Appointment.objects.filter(patient_id=patient_id).count() == 1
        assert Appointment.objects.get(patient_id=patient_id).status == AppointmentStatus.EM_ESPERA

    def test_utente_existente_reutiliza_ficha(
        self, receptionist_user, doctor_user, servico_10k
    ):
        patient = _patient(receptionist_user, first="Existente", last="Ja", doc="E2E-EXIST-001")
        before = Patient.objects.count()
        check_in = ReceptionService.check_in(patient.pk, receptionist_user)
        entry = WaitingQueue.objects.get(check_in=check_in)
        fatura = BillingService.gerar_fatura(
            receptionist_user,
            paciente_id=patient.pk,
            itens=[{"servico_id": servico_10k.pk, "quantidade": 1}],
        )
        _pay_full(receptionist_user, fatura, "10000")
        ReceptionService.assign_to_doctor(
            queue_id=entry.pk, user=receptionist_user, doctor_id=doctor_user.pk
        )
        assert Patient.objects.count() == before
        assert Appointment.objects.filter(patient=patient).count() == 1


@pytest.mark.django_db
class TestE2EImportedPatient:
    def test_importado_confirm_novo_atendimento_provenance(
        self, api_client, receptionist_user, doctor_user, servico_10k
    ):
        patient = _patient(receptionist_user, first="Historico", last="Import", doc="E2E-IMP-001")
        patient.metadata = {
            "source": "MIGRACAO_EXCEL_SAUVIDA",
            "migration_id": "MIG-E2E-001",
            "import_batch": "BATCH-E2E",
            "dados_verificados": False,
        }
        patient.save(update_fields=["metadata"])

        api_client.force_authenticate(user=receptionist_user)
        patch = api_client.patch(
            f"/api/v1/patients/{patient.pk}/",
            {"phone": "+245955882001", "address_street": "Rua Confirmada"},
            format="json",
        )
        assert patch.status_code == 200
        confirm = api_client.post(f"/api/v1/patients/{patient.pk}/confirm-imported-data/")
        assert confirm.status_code == 200
        patient.refresh_from_db()
        assert patient.metadata["migration_id"] == "MIG-E2E-001"
        assert patient.metadata["import_batch"] == "BATCH-E2E"
        assert patient.metadata["dados_verificados"] is True

        # Privacidade: sem diagnóstico em consultas; sem escrita de alergia
        allergy = api_client.post(
            f"/api/v1/patients/{patient.pk}/allergies/",
            {"allergen": "Teste", "severity": "LEVE"},
            format="json",
        )
        assert allergy.status_code == 403

        check_in = ReceptionService.check_in(patient.pk, receptionist_user)
        entry = WaitingQueue.objects.get(check_in=check_in)
        fatura = BillingService.gerar_fatura(
            receptionist_user,
            paciente_id=patient.pk,
            itens=[{"servico_id": servico_10k.pk, "quantidade": 1}],
        )
        _pay_full(receptionist_user, fatura, "10000")
        ReceptionService.assign_to_doctor(
            queue_id=entry.pk, user=receptionist_user, doctor_id=doctor_user.pk
        )


@pytest.mark.django_db
class TestE2EAppointmentArrival:
    def test_confirm_arrival_idempotent_no_duplicate(
        self, receptionist_user, doctor_user
    ):
        patient = _patient(receptionist_user, first="Marcado", last="Hoje", doc="E2E-APT-001")
        when = timezone.now() + timedelta(hours=1)
        appointment = AppointmentService.criar_consulta(
            patient_id=patient.pk,
            user=receptionist_user,
            doctor_id=doctor_user.pk,
            scheduled_at=when,
        )
        a1 = AppointmentService.confirmar_chegada(appointment.pk, receptionist_user)
        a2 = AppointmentService.confirmar_chegada(appointment.pk, receptionist_user)
        assert a1.pk == a2.pk == appointment.pk
        assert ReceptionCheckIn.objects.filter(patient=patient).count() == 1
        assert WaitingQueue.objects.filter(patient=patient).count() == 1
        assert Appointment.objects.filter(patient=patient).count() == 1


@pytest.mark.django_db
class TestE2EBillingFlows:
    def test_pagamento_integral_e_resumo(self, receptionist_user, servico_10k):
        patient = _patient(receptionist_user, first="Pago", last="Integral", doc="E2E-PAY-001")
        fatura = BillingService.gerar_fatura(
            receptionist_user,
            paciente_id=patient.pk,
            itens=[{"servico_id": servico_10k.pk, "quantidade": 1}],
        )
        _pay_full(receptionist_user, fatura, "10000")
        fatura.refresh_from_db()
        assert fatura.total_pago == Decimal("10000")
        assert fatura.total - fatura.total_pago == Decimal("0")
        hoje = timezone.localdate()
        resumo = get_resumo_operacional(data_inicio=hoje, data_fim=hoje)
        assert Decimal(resumo["total_recebido"]) >= Decimal("10000")

    def test_reducao_catalogo_intact(self, receptionist_user, servico_10k):
        cfg = SettingsService._get_singleton(ConfiguracaoFaturacao)
        cfg.permitir_reducao_rececao = True
        cfg.limite_reducao_rececao_percentual = Decimal("50")
        cfg.exigir_motivo_reducao = True
        cfg.save()
        patient = _patient(receptionist_user, first="Reducao", last="Ok", doc="E2E-RED-001")
        fatura = BillingService.gerar_fatura(
            receptionist_user,
            paciente_id=patient.pk,
            itens=[
                {
                    "servico_id": servico_10k.pk,
                    "quantidade": 1,
                    "preco_cobrado": Decimal("8000"),
                    "motivo_reducao": MotivoReducao.DIFICULDADE_FINANCEIRA,
                }
            ],
        )
        assert fatura.total == Decimal("8000")
        _pay_full(receptionist_user, fatura, "8000")
        servico_10k.refresh_from_db()
        assert servico_10k.preco == Decimal("10000")

    def test_parcial_depois_saldo_e_overpay(
        self, api_client, receptionist_user, servico_10k
    ):
        patient = _patient(receptionist_user, first="Parcial", last="Saldo", doc="E2E-PAR-001")
        fatura = BillingService.gerar_fatura(
            receptionist_user,
            paciente_id=patient.pk,
            itens=[{"servico_id": servico_10k.pk, "quantidade": 1}],
        )
        p1 = BillingService.registar_pagamento(
            fatura.pk, receptionist_user, valor=Decimal("6000"), metodo_pagamento="DINHEIRO"
        )
        BillingService.confirmar_pagamento(p1.pk, receptionist_user)
        fatura.refresh_from_db()
        assert fatura.total - fatura.total_pago == Decimal("4000")

        api_client.force_authenticate(user=receptionist_user)
        pending = api_client.get("/api/v1/billing/invoices/", {"com_saldo": True})
        assert pending.status_code == 200
        ids = [row["id"] for row in pending.data["data"]["results"]]
        assert fatura.pk in ids

        with pytest.raises(ValueError, match="superior ao saldo"):
            BillingService.registar_pagamento(
                fatura.pk, receptionist_user, valor=Decimal("5000"), metodo_pagamento="DINHEIRO"
            )
        assert Pagamento.objects.filter(fatura=fatura, valor=Decimal("5000")).count() == 0

        p2 = BillingService.registar_pagamento(
            fatura.pk, receptionist_user, valor=Decimal("4000"), metodo_pagamento="DINHEIRO"
        )
        BillingService.confirmar_pagamento(p2.pk, receptionist_user)
        fatura.refresh_from_db()
        assert fatura.total - fatura.total_pago == Decimal("0")
        assert Recibo.objects.filter(pagamento__fatura=fatura).count() == 2

    def test_cancelar_fatura_sem_saldo_activo(self, api_client, receptionist_user, servico_10k):
        patient = _patient(receptionist_user, first="Cancel", last="Fat", doc="E2E-CAN-001")
        fatura = BillingService.gerar_fatura(
            receptionist_user,
            paciente_id=patient.pk,
            itens=[{"servico_id": servico_10k.pk, "quantidade": 1}],
        )
        BillingService.cancelar_fatura(fatura.pk, receptionist_user)
        fatura.refresh_from_db()
        assert fatura.estado == FaturaEstado.CANCELADA
        assert Fatura.objects.filter(pk=fatura.pk).exists()
        api_client.force_authenticate(user=receptionist_user)
        pending = api_client.get("/api/v1/billing/invoices/", {"com_saldo": True})
        ids = [row["id"] for row in pending.data["data"]["results"]]
        assert fatura.pk not in ids


@pytest.mark.django_db
class TestE2EQueueAndNoDoctor:
    def test_fila_posicoes(self, receptionist_user):
        p1 = _patient(receptionist_user, first="Fila", last="Um", phone="+245955883001", doc="E2E-Q1")
        p2 = _patient(receptionist_user, first="Fila", last="Dois", phone="+245955883002", doc="E2E-Q2")
        ReceptionService.check_in(p1.pk, receptionist_user)
        ReceptionService.check_in(p2.pk, receptionist_user)
        entries = list(WaitingQueue.objects.filter(status=QueueStatus.WAITING).order_by("position"))
        assert len(entries) >= 2
        assert entries[0].position == 1
        assert entries[1].position == 2

    def test_sem_medico_nao_perde_paciente_nem_pagamento(
        self, receptionist_user, servico_10k
    ):
        """Sem médico activo: falha controlada; fila e pagamento intactos."""
        patient = _patient(receptionist_user, first="Sem", last="Medico", doc="E2E-NOD-001")
        check_in = ReceptionService.check_in(patient.pk, receptionist_user)
        entry = WaitingQueue.objects.get(check_in=check_in)
        fatura = BillingService.gerar_fatura(
            receptionist_user,
            paciente_id=patient.pk,
            itens=[{"servico_id": servico_10k.pk, "quantidade": 1}],
        )
        _pay_full(receptionist_user, fatura, "10000")

        with pytest.raises(ValueError, match="médico"):
            ReceptionService.assign_to_doctor(queue_id=entry.pk, user=receptionist_user)

        entry.refresh_from_db()
        check_in.refresh_from_db()
        fatura.refresh_from_db()
        assert entry.status == QueueStatus.WAITING
        assert check_in.status == "WAITING"
        assert fatura.estado == FaturaEstado.PAGA
        assert Appointment.objects.filter(patient=patient).count() == 0
        assert Recibo.objects.filter(pagamento__fatura=fatura).exists()


@pytest.mark.django_db
class TestE2EPrivacyDoctorOk:
    def test_medico_escreve_alergia_rececao_nao(
        self, api_client, receptionist_user, doctor_user
    ):
        patient = _patient(receptionist_user, first="Priv", last="Ok", doc="E2E-PRIV-001")
        api_client.force_authenticate(user=receptionist_user)
        assert (
            api_client.post(
                f"/api/v1/patients/{patient.pk}/allergies/",
                {"allergen": "X", "severity": "LEVE"},
                format="json",
            ).status_code
            == 403
        )
        api_client.force_authenticate(user=doctor_user)
        assert (
            api_client.post(
                f"/api/v1/patients/{patient.pk}/allergies/",
                {"allergen": "Penicilina", "severity": "GRAVE"},
                format="json",
            ).status_code
            == 201
        )
        assert PatientAllergy.objects.filter(patient=patient, allergen="Penicilina").exists()
