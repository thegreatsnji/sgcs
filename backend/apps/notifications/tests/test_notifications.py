"""Testes do módulo de notificações."""

import pytest
from django.core import mail
from django.core.cache import cache
from django.urls import reverse
from rest_framework import status

from apps.audit_logs.models import AuditAction, AuditLog
from apps.authentication.models import User, UserRole
from apps.notifications.constants import NotificacaoCanal, NotificacaoEstado, NotificacaoTipo
from apps.notifications.models import Notificacao, TemplateEmail, TemplateSMS
from apps.notifications.services.notification_service import NotificationService
from apps.notifications.services.preference_service import NotificationPreferenceService
from apps.notifications.services.queue_service import NotificationQueueService
from apps.notifications.services.template_service import TemplateService
from core.events.event_bus import event_bus
from core.events.events import EventNames


@pytest.fixture(autouse=True)
def email_locmem(settings):
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"


@pytest.fixture(autouse=True)
def clear_notification_cache():
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def medico_user(db):
    return User.objects.create_user(
        email="medico.notif@test.com",
        password="Test1234!",
        first_name="Médico",
        last_name="Notif",
        role=UserRole.MEDICO,
    )


@pytest.mark.django_db
class TestNotificationService:
    def test_criar_notificacao_interna(self, medico_user):
        notif = NotificationService.criar(
            titulo="Teste",
            mensagem="Mensagem de teste",
            utilizador=medico_user,
            canal=NotificacaoCanal.INTERNO,
        )
        assert notif is not None
        assert notif.estado == NotificacaoEstado.ENTREGUE
        assert AuditLog.objects.filter(action=AuditAction.NOTIFICACAO_CRIADA).exists()

    def test_marcar_lida(self, medico_user):
        notif = NotificationService.criar(
            titulo="Ler",
            mensagem="Conteúdo",
            utilizador=medico_user,
            canal=NotificacaoCanal.INTERNO,
        )
        NotificationService.marcar_lida(notif.pk, medico_user)
        notif.refresh_from_db()
        assert notif.lida is True
        assert AuditLog.objects.filter(action=AuditAction.NOTIFICACAO_LIDA).exists()

    def test_contador_nao_lidas(self, medico_user):
        NotificationService.criar(
            titulo="A",
            mensagem="B",
            utilizador=medico_user,
            canal=NotificacaoCanal.INTERNO,
        )
        assert NotificationService.contador_nao_lidas(medico_user) == 1

    def test_respeita_preferencias(self, medico_user):
        pref = NotificationPreferenceService.obter_ou_criar(medico_user)
        pref.receber_internas = False
        pref.save()
        notif = NotificationService.criar(
            titulo="Bloqueada",
            mensagem="Não deve criar",
            utilizador=medico_user,
            canal=NotificacaoCanal.INTERNO,
        )
        assert notif is None


@pytest.mark.django_db
class TestNotificationsAPI:
    def test_list_requires_auth(self, api_client):
        response = api_client.get(reverse("notifications:notification-list"))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_notification(self, api_client, admin_user):
        api_client.force_authenticate(user=admin_user)
        response = api_client.post(
            reverse("notifications:notification-list"),
            {"titulo": "Nova", "mensagem": "Alerta clínico"},
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["success"] is True

    def test_unread_endpoint(self, api_client, medico_user):
        api_client.force_authenticate(user=medico_user)
        NotificationService.criar(
            titulo="Não lida",
            mensagem="Teste",
            utilizador=medico_user,
            canal=NotificacaoCanal.INTERNO,
        )
        response = api_client.get(reverse("notifications:notification-unread"))
        assert response.status_code == status.HTTP_200_OK
        assert response.data["data"]["contador"] >= 1

    def test_mark_read(self, api_client, medico_user):
        api_client.force_authenticate(user=medico_user)
        notif = NotificationService.criar(
            titulo="Ler via API",
            mensagem="Teste",
            utilizador=medico_user,
            canal=NotificacaoCanal.INTERNO,
        )
        response = api_client.post(reverse("notifications:notification-read", args=[notif.pk]))
        assert response.status_code == status.HTTP_200_OK

    def test_history_endpoint(self, api_client, medico_user):
        api_client.force_authenticate(user=medico_user)
        response = api_client.get(reverse("notifications:notification-history"))
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestTemplatesAPI:
    def test_create_email_template(self, api_client, admin_user):
        api_client.force_authenticate(user=admin_user)
        response = api_client.post(
            reverse("notifications:template-email-list"),
            {
                "codigo": "consulta-confirmada",
                "nome": "Consulta confirmada",
                "assunto": "Consulta {{data}}",
                "corpo": "Olá {{nome}}, consulta {{consulta}} às {{hora}}.",
            },
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert AuditLog.objects.filter(action=AuditAction.TEMPLATE_CRIADO).exists()

    def test_preview_template(self, api_client, admin_user):
        template = TemplateEmail.objects.create(
            codigo="preview-test",
            nome="Preview",
            assunto="Olá {{nome}}",
            corpo="Clínica {{clinica}}",
        )
        api_client.force_authenticate(user=admin_user)
        response = api_client.post(
            reverse("notifications:template-email-preview", args=[template.pk]),
            {"contexto": {"nome": "João", "clinica": "SauVida"}},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert "João" in response.data["data"]["assunto"]

    def test_template_render(self):
        texto = TemplateService.renderizar_texto(
            "Consulta {{consulta}} em {{data}}",
            {"consulta": "CON-001", "data": "10/07/2026"},
        )
        assert "CON-001" in texto


@pytest.mark.django_db
class TestPreferencesAPI:
    def test_get_preferences(self, api_client, medico_user):
        api_client.force_authenticate(user=medico_user)
        response = api_client.get(reverse("notifications:preferences"))
        assert response.status_code == status.HTTP_200_OK
        assert "receber_email" in response.data["data"]

    def test_update_preferences(self, api_client, medico_user):
        api_client.force_authenticate(user=medico_user)
        response = api_client.patch(
            reverse("notifications:preferences"),
            {"receber_sms": True},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert AuditLog.objects.filter(action=AuditAction.PREFERENCIA_ALTERADA).exists()


@pytest.mark.django_db
class TestEmailSMS:
    def test_send_test_email(self, api_client, admin_user):
        mail.outbox = []
        api_client.force_authenticate(user=admin_user)
        response = api_client.post(
            reverse("notifications:notification-email-test"),
            {"destinatario": "teste@sgcs.local"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(mail.outbox) == 1
        assert AuditLog.objects.filter(action=AuditAction.EMAIL_ENVIADO).exists()

    def test_sms_history(self, api_client, admin_user):
        api_client.force_authenticate(user=admin_user)
        api_client.post(
            reverse("notifications:notification-sms-test"),
            {"telefone": "+245900000000"},
            format="json",
        )
        response = api_client.get(reverse("notifications:notification-sms-history"))
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestQueueAndCelery:
    def test_enfileirar_email(self, medico_user):
        notif = Notificacao.objects.create(
            utilizador=medico_user,
            titulo="E-mail",
            mensagem="Corpo",
            canal=NotificacaoCanal.EMAIL,
            destinatario_email=medico_user.email,
        )
        item = NotificationQueueService.enfileirar(notif)
        assert item.notificacao_id == notif.pk

    def test_processar_fila(self, medico_user):
        notif = Notificacao.objects.create(
            utilizador=medico_user,
            titulo="Processar",
            mensagem="Fila",
            canal=NotificacaoCanal.INTERNO,
        )
        NotificationQueueService.enfileirar(notif)
        processados = NotificationQueueService.processar_pendentes()
        assert processados >= 1

    def test_celery_tasks(self):
        from apps.notifications.tasks import (
            limpar_notificacoes_antigas,
            processar_fila,
            reenviar_falhas,
        )

        assert processar_fila()["status"] == "ok"
        assert reenviar_falhas()["status"] == "ok"
        assert limpar_notificacoes_antigas()["status"] == "ok"


@pytest.mark.django_db
class TestEventBusIntegration:
    def test_patient_created_event(self, medico_user):
        event_bus.publish(EventNames.PATIENT_CREATED, {"patient_id": 1})
        assert Notificacao.objects.filter(evento_origem=EventNames.PATIENT_CREATED).exists()


@pytest.mark.django_db
class TestNotificationsRBAC:
    def test_receptionist_denied_template(self, api_client, receptionist_user):
        api_client.force_authenticate(user=receptionist_user)
        response = api_client.get(reverse("notifications:template-email-list"))
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_medico_can_view(self, api_client, medico_user):
        api_client.force_authenticate(user=medico_user)
        response = api_client.get(reverse("notifications:notification-list"))
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestNotificationsDashboard:
    def test_dashboard_kpis(self, api_client, admin_user):
        api_client.force_authenticate(user=admin_user)
        response = api_client.get("/api/v1/dashboard/notifications/")
        assert response.status_code == status.HTTP_200_OK
        assert "total" in response.data["data"]

    def test_dashboard_cache(self, admin_user):
        k1 = NotificationService.dashboard_kpis()
        k2 = NotificationService.dashboard_kpis()
        assert k1 == k2


@pytest.mark.django_db
class TestTemplateSMS:
    def test_create_sms_template(self, api_client, admin_user):
        api_client.force_authenticate(user=admin_user)
        response = api_client.post(
            reverse("notifications:template-sms-list"),
            {
                "codigo": "lembrete-consulta",
                "nome": "Lembrete",
                "mensagem": "Lembrete: {{data}} às {{hora}}",
            },
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert TemplateSMS.objects.filter(codigo="lembrete-consulta").exists()
