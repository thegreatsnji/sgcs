"""Serviço de envio de e-mail."""

from django.conf import settings
from django.core.mail import send_mail

from apps.audit_logs.models import AuditAction
from apps.audit_logs.services import AuditService
from apps.notifications.constants import NotificacaoEstado
from apps.notifications.models import HistoricoEmail, Notificacao
from apps.notifications.services.cache_service import NotificationCacheService


class EmailService:
    @staticmethod
    def enviar(
        *,
        destinatario: str,
        assunto: str,
        corpo: str,
        notificacao: Notificacao | None = None,
        user=None,
        request=None,
    ) -> HistoricoEmail:
        estado = NotificacaoEstado.ENVIADA
        erro = ""
        try:
            send_mail(
                subject=assunto,
                message=corpo,
                from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@sgcs.local"),
                recipient_list=[destinatario],
                fail_silently=False,
            )
        except Exception as exc:  # noqa: BLE001
            estado = NotificacaoEstado.FALHOU
            erro = str(exc)

        historico = HistoricoEmail.objects.create(
            destinatario=destinatario,
            assunto=assunto,
            corpo=corpo,
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
            action=AuditAction.EMAIL_ENVIADO,
            user=user,
            request=request,
            description=f"E-mail enviado para {destinatario}.",
            resource_type="historico_email",
            resource_id=str(historico.pk),
            metadata={"estado": estado},
        )
        NotificationCacheService.invalidate_dashboard()
        return historico

    @staticmethod
    def enviar_teste(destinatario: str, user, request=None) -> HistoricoEmail:
        return EmailService.enviar(
            destinatario=destinatario,
            assunto="SGCS — E-mail de teste",
            corpo="Este é um e-mail de teste do sistema SGCS.",
            user=user,
            request=request,
        )
