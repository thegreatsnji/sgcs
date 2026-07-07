"""Serviço de preferências de notificação."""

from apps.authentication.models import User
from apps.audit_logs.models import AuditAction
from apps.audit_logs.services import AuditService
from apps.notifications.models import PreferenciaNotificacao


class NotificationPreferenceService:
    @staticmethod
    def obter_ou_criar(utilizador: User) -> PreferenciaNotificacao:
        pref, _ = PreferenciaNotificacao.objects.get_or_create(utilizador=utilizador)
        return pref

    @staticmethod
    def actualizar(utilizador: User, data: dict, request=None) -> PreferenciaNotificacao:
        pref = NotificationPreferenceService.obter_ou_criar(utilizador)
        campos = [
            "receber_email",
            "receber_sms",
            "receber_internas",
            "receber_lembretes",
            "receber_alertas_admin",
        ]
        for campo in campos:
            if campo in data:
                setattr(pref, campo, data[campo])
        pref.save()
        AuditService.log(
            action=AuditAction.PREFERENCIA_ALTERADA,
            user=utilizador,
            request=request,
            description="Preferências de notificação actualizadas.",
            resource_type="preferencia_notificacao",
            resource_id=str(pref.pk),
            metadata=data,
        )
        return pref

    @staticmethod
    def pode_receber(utilizador: User | None, *, canal: str, tipo: str) -> bool:
        if not utilizador:
            return False
        pref = NotificationPreferenceService.obter_ou_criar(utilizador)
        if tipo == "LEMBRETE" and not pref.receber_lembretes:
            return False
        if canal == "INTERNO":
            return pref.receber_internas
        if canal == "EMAIL":
            return pref.receber_email
        if canal == "SMS":
            return pref.receber_sms
        return True
