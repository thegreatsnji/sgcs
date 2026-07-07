"""Testes do módulo de configurações."""

import pytest
from django.core.cache import cache
from django.urls import reverse
from rest_framework import status

from apps.authentication.models import User, UserRole
from apps.audit_logs.models import AuditAction, AuditLog
from apps.settings.models import (
    BackupRegisto,
    Consultorio,
    Departamento,
    EspecialidadeMedica,
    FeatureFlag,
    TipoConsulta,
)
from apps.settings.services.backup_service import BackupService
from apps.settings.services.settings_service import SettingsService


@pytest.fixture(autouse=True)
def clear_settings_cache():
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def director_settings(db):
    return User.objects.create_user(
        email="director.settings@test.com",
        password="Test1234!",
        first_name="Director",
        last_name="Settings",
        role=UserRole.DIRECTOR,
    )


@pytest.fixture
def department(db):
    return Departamento.objects.create(codigo="REC", nome="Receção")


@pytest.mark.django_db
class TestClinicSettings:
    def test_get_clinic_profile(self):
        data = SettingsService.get_clinic_profile()
        assert "nome" in data

    def test_update_clinic_profile(self, admin_user):
        data = SettingsService.update_clinic_profile(
            {"nome": "Clínica Teste", "cidade": "Bissau"},
            user=admin_user,
        )
        assert data["nome"] == "Clínica Teste"
        assert AuditLog.objects.filter(action=AuditAction.SETTINGS_UPDATED).exists()

    def test_clinic_api(self, api_client, admin_user):
        api_client.force_authenticate(user=admin_user)
        response = api_client.get(reverse("settings:clinic"))
        assert response.status_code == status.HTTP_200_OK

    def test_clinic_patch_api(self, api_client, admin_user):
        api_client.force_authenticate(user=admin_user)
        response = api_client.patch(reverse("settings:clinic"), {"nome": "Nova Clínica"}, format="json")
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestSpecialties:
    def test_create_specialty(self, department):
        esp = EspecialidadeMedica.objects.create(codigo="MED", nome="Medicina Geral")
        assert esp.activo is True

    def test_specialties_api_list(self, api_client, admin_user):
        api_client.force_authenticate(user=admin_user)
        response = api_client.get(reverse("settings:specialty-list"))
        assert response.status_code == status.HTTP_200_OK

    def test_specialties_api_create(self, api_client, admin_user):
        api_client.force_authenticate(user=admin_user)
        response = api_client.post(
            reverse("settings:specialty-list"),
            {"codigo": "CARD", "nome": "Cardiologia", "cor": "#ff0000"},
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
class TestDepartments:
    def test_departments_crud_api(self, api_client, admin_user):
        api_client.force_authenticate(user=admin_user)
        create = api_client.post(
            reverse("settings:department-list"),
            {"codigo": "LAB", "nome": "Laboratório"},
            format="json",
        )
        assert create.status_code == status.HTTP_201_CREATED
        dept_id = create.data["data"]["id"]
        detail = api_client.get(reverse("settings:department-detail", args=[dept_id]))
        assert detail.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestRooms:
    def test_room_api(self, api_client, admin_user, department):
        api_client.force_authenticate(user=admin_user)
        response = api_client.post(
            reverse("settings:room-list"),
            {
                "numero": "S01",
                "nome": "Sala 1",
                "departamento": department.pk,
                "capacidade": 2,
            },
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert Consultorio.objects.filter(numero="S01").exists()


@pytest.mark.django_db
class TestConsultationTypes:
    def test_consultation_type_api(self, api_client, admin_user):
        api_client.force_authenticate(user=admin_user)
        response = api_client.post(
            reverse("settings:consultation-type-list"),
            {
                "codigo": "URG",
                "nome": "Urgência",
                "duracao_minutos": 20,
                "preco_base": "5000.00",
            },
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert TipoConsulta.objects.filter(codigo="URG").exists()


@pytest.mark.django_db
class TestBillingSecurityEmail:
    def test_billing_config(self, api_client, admin_user):
        api_client.force_authenticate(user=admin_user)
        get_r = api_client.get(reverse("settings:billing"))
        assert get_r.status_code == status.HTTP_200_OK
        patch_r = api_client.patch(reverse("settings:billing"), {"iva_percentagem": "5.00"}, format="json")
        assert patch_r.status_code == status.HTTP_200_OK

    def test_security_config(self, api_client, admin_user):
        api_client.force_authenticate(user=admin_user)
        response = api_client.get(reverse("settings:security"))
        assert response.status_code == status.HTTP_200_OK
        patch = api_client.patch(
            reverse("settings:security"),
            {"max_login_attempts": 3},
            format="json",
        )
        assert patch.status_code == status.HTTP_200_OK
        assert AuditLog.objects.filter(action=AuditAction.SECURITY_CONFIGURATION).exists()

    def test_email_config(self, api_client, admin_user):
        api_client.force_authenticate(user=admin_user)
        response = api_client.patch(
            reverse("settings:email"),
            {"host": "smtp.test.com", "port": 587},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK

    def test_email_test(self, api_client, admin_user):
        api_client.force_authenticate(user=admin_user)
        response = api_client.post(reverse("settings:email-test"))
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestFeatureFlags:
    def test_feature_flags_api(self, api_client, admin_user):
        SettingsService.ensure_feature_flags()
        api_client.force_authenticate(user=admin_user)
        get_r = api_client.get(reverse("settings:feature-flags"))
        assert get_r.status_code == status.HTTP_200_OK
        patch_r = api_client.patch(
            reverse("settings:feature-flags"),
            {"codigo": "laboratorio", "activo": False},
            format="json",
        )
        assert patch_r.status_code == status.HTTP_200_OK
        assert FeatureFlag.objects.get(codigo="laboratorio").activo is False

    def test_feature_flag_audit(self, api_client, admin_user):
        SettingsService.ensure_feature_flags()
        api_client.force_authenticate(user=admin_user)
        api_client.patch(
            reverse("settings:feature-flags"),
            {"codigo": "financeiro", "activo": True},
            format="json",
        )
        assert AuditLog.objects.filter(action=AuditAction.FEATURE_FLAG_UPDATED).exists()


@pytest.mark.django_db
class TestBackups:
    def test_create_backup(self, admin_user):
        backup = BackupService.criar_backup(BackupRegisto.TIPO_MANUAL, user=admin_user)
        assert backup.estado == BackupRegisto.ESTADO_CONCLUIDO

    def test_backup_api(self, api_client, admin_user):
        api_client.force_authenticate(user=admin_user)
        response = api_client.post(reverse("settings:backup-list"), {"tipo": "MANUAL"}, format="json")
        assert response.status_code == status.HTTP_201_CREATED

    def test_backup_restore_api(self, api_client, admin_user):
        backup = BackupService.criar_backup(BackupRegisto.TIPO_MANUAL, user=admin_user)
        api_client.force_authenticate(user=admin_user)
        response = api_client.post(reverse("settings:backup-restore", args=[backup.pk]))
        assert response.status_code == status.HTTP_200_OK
        assert AuditLog.objects.filter(action=AuditAction.BACKUP_RESTORED).exists()


@pytest.mark.django_db
class TestSystemDashboard:
    def test_monitoring_api(self, api_client, admin_user):
        api_client.force_authenticate(user=admin_user)
        response = api_client.get(reverse("settings:monitoring"))
        assert response.status_code == status.HTTP_200_OK
        assert "database" in response.data["data"]

    def test_system_dashboard(self, api_client, admin_user):
        api_client.force_authenticate(user=admin_user)
        response = api_client.get(reverse("dashboard:system"))
        assert response.status_code == status.HTTP_200_OK
        assert "monitorizacao" in response.data["data"]

    def test_system_dashboard_director(self, api_client, director_settings):
        api_client.force_authenticate(user=director_settings)
        response = api_client.get(reverse("dashboard:system"))
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestSettingsRBAC:
    def test_receptionist_denied(self, api_client, receptionist_user):
        api_client.force_authenticate(user=receptionist_user)
        response = api_client.get(reverse("settings:clinic"))
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_director_allowed(self, api_client, director_settings):
        api_client.force_authenticate(user=director_settings)
        response = api_client.get(reverse("settings:clinic"))
        assert response.status_code == status.HTTP_200_OK

    def test_admin_full_access(self, api_client, admin_user):
        api_client.force_authenticate(user=admin_user)
        assert api_client.get(reverse("settings:security")).status_code == status.HTTP_200_OK
        assert api_client.get(reverse("settings:feature-flags")).status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestSettingsTasks:
    def test_celery_stubs(self):
        from apps.settings.tasks import (
            backup_database,
            cleanup_logs,
            cleanup_storage,
            restore_database,
            send_test_email,
        )

        assert backup_database(1)["status"] == "stub"
        assert restore_database(1)["status"] == "stub"
        assert send_test_email()["status"] == "stub"
        assert cleanup_storage()["status"] == "stub"
        assert cleanup_logs()["status"] == "stub"


@pytest.mark.django_db
class TestWorkingHoursAndHolidays:
    def test_working_hours_api(self, api_client, admin_user):
        api_client.force_authenticate(user=admin_user)
        response = api_client.post(
            reverse("settings:working-hours-list"),
            {"dia_semana": "SEG", "hora_abertura": "08:00", "hora_encerramento": "18:00"},
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED

    def test_holidays_api(self, api_client, admin_user):
        api_client.force_authenticate(user=admin_user)
        response = api_client.post(
            reverse("settings:holiday-list"),
            {"data": "2026-12-25", "nome": "Natal"},
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED

    def test_lab_exam_types_api(self, api_client, admin_user):
        api_client.force_authenticate(user=admin_user)
        response = api_client.post(
            reverse("settings:lab-exam-type-list"),
            {"codigo": "HEM", "nome": "Hemograma", "categoria": "SANGUE"},
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED

    def test_files_settings_api(self, api_client, admin_user):
        api_client.force_authenticate(user=admin_user)
        response = api_client.get(reverse("settings:files"))
        assert response.status_code == status.HTTP_200_OK

    def test_sms_settings_api(self, api_client, admin_user):
        api_client.force_authenticate(user=admin_user)
        response = api_client.get(reverse("settings:sms"))
        assert response.status_code == status.HTTP_200_OK

    def test_settings_cache(self):
        SettingsService.get_clinic_profile()
        assert SettingsService.get_clinic_profile()["nome"]
