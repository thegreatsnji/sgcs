"""Serviço de envio de SMS (simulado em desenvolvimento)."""

import logging

from apps.audit_logs.models import AuditAction
from apps.audit_logs.services import AuditService
from apps.notifications.constants import NotificacaoEstado
from apps.notifications.models import HistoricoSMS, Notificacao
from apps.notifications.services.cache_service import NotificationCacheService

logger = logging.getLogger(__name__)


class SMSService:
    @staticmethod
    def enviar(
        *,
        telefone: str,
        mensagem: str,
        notificacao: Notificacao | None = None,
        user=None,
        request=None,
    ) -> HistoricoSMS:
        estado = NotificacaoEstado.ENTREGUE
        erro = ""
        try:
            logger.info("SMS SGCS para %s: %s", telefone, mensagem[:80])
        except Exception as exc:  # noqa: BLE001
            estado = NotificacaoEstado.FALHOU
            erro = str(exc)

        historico = HistoricoSMS.objects.create(
            telefone=telefone,
            mensagem=mensagem,
            estado=estado,
            erro=erro,
            notificacao=notificacao,
        )
        if notificacao:
            notificacao.estado = estado
            notificacao.save(update_fields=["estado", "updated_at"])
            if notificacao.utilizador_id:
                NotificationCacheService.invalidate_user(notificacao.utilizador_id)

        AuditService.log(
            action=AuditAction.SMS_ENVIADO,
            user=user,
            request=request,
            description=f"SMS enviado para {telefone}.",
            resource_type="historico_sms",
            resource_id=str(historico.pk),
            metadata={"estado": estado},
        )
        NotificationCacheService.invalidate_dashboard()
        return historico

    @staticmethod
    def enviar_teste(telefone: str, user, request=None) -> HistoricoSMS:
        return SMSService.enviar(
            telefone=telefone,
            mensagem="SGCS — SMS de teste.",
            user=user,
            request=request,
        )
