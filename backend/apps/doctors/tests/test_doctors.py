"""Testes do módulo médico."""

import pytest
from datetime import date, timedelta
from django.core.cache import cache
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from apps.appointments.constants import AppointmentStatus
from apps.appointments.models import Appointment
from apps.audit_logs.models import AuditAction, AuditLog
from apps.authentication.models import User, UserRole
from apps.doctors.constants import PrescricaoEstado, TratamentoEstado
from apps.doctors.models import Prescricao, Tratamento
from apps.doctors.services.prescription_service import PrescriptionService
from apps.patients.models import Patient


@pytest.fixture(autouse=True)
def clear_doctors_cache():
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def doctor_user(db):
    return User.objects.create_user(
        email="medico.doctors@test.com",
        password="Test1234!",
        first_name="Médico",
        last_name="Teste",
        role=UserRole.MEDICO,
    )


@pytest.fixture
def patient_doctor(db, admin_user):
    return Patient.objects.create(
        first_name="João",
        last_name="Médico",
        birth_date="1985-03-10",
        gender="M",
        phone="955111222",
        created_by=admin_user,
    )


@pytest.fixture
def consulta_doctor(db, doctor_user, patient_doctor):
    return Appointment.objects.create(
        patient=patient_doctor,
        doctor=doctor_user,
        appointment_number="CON-DOC-001",
        scheduled_at=timezone.now(),
        consultation_date=timezone.localdate(),
        status=AppointmentStatus.EM_CONSULTA,
        created_by=doctor_user,
    )


@pytest.mark.django_db
class TestPrescriptionService:
    def test_criar_prescricao(self, doctor_user, consulta_doctor):
        prescricao = PrescriptionService.criar_prescricao(
            consulta_id=consulta_doctor.pk,
            medico=doctor_user,
            data={
                "medicamentos": [
                    {
                        "nome": "Paracetamol",
                        "dosagem": "500mg",
                        "frequencia": "2x por dia",
                        "duracao": "7 dias",
                        "posologia": "1 comprimido antes das refeições",
                    }
                ]
            },
        )
        assert prescricao.medicamentos.count() == 1
        assert AuditLog.objects.filter(action=AuditAction.PRESCRICAO_CRIADA).exists()

    def test_aprovar_prescricao(self, doctor_user, consulta_doctor):
        prescricao = PrescriptionService.criar_prescricao(
            consulta_id=consulta_doctor.pk,
            medico=doctor_user,
            data={},
        )
        PrescriptionService.aprovar_prescricao(prescricao.pk, doctor_user)
        prescricao.refresh_from_db()
        assert prescricao.estado == PrescricaoEstado.APROVADA


@pytest.mark.django_db
class TestPrescriptionsAPI:
    def test_list_requires_auth(self, api_client):
        response = api_client.get(reverse("prescriptions:prescription-list"))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_prescription(self, api_client, doctor_user, consulta_doctor):
        api_client.force_authenticate(user=doctor_user)
        response = api_client.post(
            reverse("prescriptions:prescription-list"),
            {
                "consulta_id": consulta_doctor.pk,
                "medicamentos": [
                    {
                        "nome": "Amoxicilina",
                        "dosagem": "500mg",
                        "frequencia": "3x dia",
                        "duracao": "5 dias",
                    }
                ],
            },
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["success"] is True

    def test_approve_prescription(self, api_client, doctor_user, consulta_doctor):
        api_client.force_authenticate(user=doctor_user)
        create = api_client.post(
            reverse("prescriptions:prescription-list"),
            {"consulta_id": consulta_doctor.pk},
            format="json",
        )
        pid = create.data["data"]["id"]
        response = api_client.post(reverse("prescriptions:prescription-approve", args=[pid]))
        assert response.status_code == status.HTTP_200_OK

    def test_history(self, api_client, doctor_user, consulta_doctor, patient_doctor):
        api_client.force_authenticate(user=doctor_user)
        api_client.post(
            reverse("prescriptions:prescription-list"),
            {"consulta_id": consulta_doctor.pk},
            format="json",
        )
        response = api_client.get(
            reverse("prescriptions:prescription-history"),
            {"paciente_id": patient_doctor.pk},
        )
        assert response.status_code == status.HTTP_200_OK
        assert "prescricoes" in response.data["data"]


@pytest.mark.django_db
class TestTreatmentsAPI:
    def test_create_treatment(self, api_client, doctor_user, consulta_doctor):
        api_client.force_authenticate(user=doctor_user)
        response = api_client.post(
            reverse("treatments:treatment-list"),
            {
                "consulta_id": consulta_doctor.pk,
                "tipo": "Fisioterapia",
                "descricao": "Sessões de reabilitação",
                "data_inicio": date.today().isoformat(),
            },
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert Tratamento.objects.count() == 1

    def test_finish_treatment(self, api_client, doctor_user, consulta_doctor):
        api_client.force_authenticate(user=doctor_user)
        create = api_client.post(
            reverse("treatments:treatment-list"),
            {
                "consulta_id": consulta_doctor.pk,
                "tipo": "Curativo",
                "descricao": "Troca diária",
                "data_inicio": date.today().isoformat(),
            },
            format="json",
        )
        tid = create.data["data"]["id"]
        response = api_client.post(reverse("treatments:treatment-finish", args=[tid]))
        assert response.status_code == status.HTTP_200_OK
        assert Tratamento.objects.get(pk=tid).estado == TratamentoEstado.CONCLUIDO


@pytest.mark.django_db
class TestEvolutionsAPI:
    def test_create_evolution(self, api_client, doctor_user, consulta_doctor):
        api_client.force_authenticate(user=doctor_user)
        response = api_client.post(
            reverse("evolutions:evolution-list"),
            {
                "consulta_id": consulta_doctor.pk,
                "tipo": "MELHORIA",
                "observacoes": "Paciente com melhoria significativa",
            },
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert AuditLog.objects.filter(action=AuditAction.EVOLUCAO_ADICIONADA).exists()


@pytest.mark.django_db
class TestDischargesAPI:
    def test_create_discharge(self, api_client, doctor_user, consulta_doctor):
        api_client.force_authenticate(user=doctor_user)
        response = api_client.post(
            reverse("discharges:discharge-list"),
            {
                "consulta_id": consulta_doctor.pk,
                "motivo": "Recuperação completa",
                "condicao": "Estável",
                "recomendacoes": "Repouso relativo",
            },
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert AuditLog.objects.filter(action=AuditAction.ALTA_MEDICA).exists()


@pytest.mark.django_db
class TestFollowupsAPI:
    def test_create_followup(self, api_client, doctor_user, consulta_doctor):
        api_client.force_authenticate(user=doctor_user)
        data_prevista = (date.today() + timedelta(days=14)).isoformat()
        response = api_client.post(
            reverse("followups:followup-list"),
            {
                "consulta_id": consulta_doctor.pk,
                "data_prevista": data_prevista,
                "motivo": "Reavaliação",
            },
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["data"]["consulta_agendada_numero"]


@pytest.mark.django_db
class TestDoctorsRBAC:
    def test_receptionist_denied(self, api_client, receptionist_user):
        api_client.force_authenticate(user=receptionist_user)
        response = api_client.get(reverse("prescriptions:prescription-list"))
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_doctor_allowed(self, api_client, doctor_user):
        api_client.force_authenticate(user=doctor_user)
        response = api_client.get(reverse("prescriptions:prescription-list"))
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestDoctorsTasks:
    def test_celery_stubs(self):
        from apps.doctors.tasks import (
            enviar_prescricao_email,
            gerar_relatorio_alta,
            lembrar_seguimento,
        )

        assert enviar_prescricao_email(1)["status"] == "stub"
        assert lembrar_seguimento(1)["status"] == "stub"
        assert gerar_relatorio_alta(1)["status"] == "stub"


@pytest.mark.django_db
class TestPrescriptionFinish:
    def test_finish_prescription_api(self, api_client, doctor_user, consulta_doctor):
        api_client.force_authenticate(user=doctor_user)
        create = api_client.post(
            reverse("prescriptions:prescription-list"),
            {"consulta_id": consulta_doctor.pk},
            format="json",
        )
        pid = create.data["data"]["id"]
        api_client.post(reverse("prescriptions:prescription-approve", args=[pid]))
        response = api_client.post(reverse("prescriptions:prescription-finish", args=[pid]))
        assert response.status_code == status.HTTP_200_OK
        assert Prescricao.objects.get(pk=pid).estado == PrescricaoEstado.CONCLUIDA


@pytest.mark.django_db
class TestDoctorsCache:
    def test_historico_cache(self, doctor_user, consulta_doctor, patient_doctor):
        PrescriptionService.criar_prescricao(
            consulta_id=consulta_doctor.pk,
            medico=doctor_user,
            data={},
        )
        from apps.doctors.services.cache_service import DoctorsCacheService

        DoctorsCacheService.invalidate_historico(patient_doctor.pk)
        h1 = PrescriptionService.historico_paciente(patient_doctor.pk)
        h2 = PrescriptionService.historico_paciente(patient_doctor.pk)
        assert h1 == h2
        assert len(h1["prescricoes"]) == 1
        assert DoctorsCacheService.get_historico(patient_doctor.pk) is not None


@pytest.mark.django_db
class TestPlanoTerapeutico:
    def test_criar_com_plano(self, doctor_user, consulta_doctor):
        from apps.doctors.models import PlanoTerapeutico

        prescricao = PrescriptionService.criar_prescricao(
            consulta_id=consulta_doctor.pk,
            medico=doctor_user,
            data={
                "plano": {
                    "descricao": "Fisioterapia 2x/semana",
                    "objectivos": "Recuperação funcional",
                    "duracao_prevista": "4 semanas",
                }
            },
        )
        assert PlanoTerapeutico.objects.filter(prescricao=prescricao).exists()
