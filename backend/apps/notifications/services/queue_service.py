"""Serviço de fila de notificações."""

from django.db import transaction
from django.db.models import F
from django.utils import timezone

from apps.notifications.constants import NotificacaoEstado
from apps.notifications.models import FilaNotificacao, Notificacao
from apps.notifications.services.cache_service import NotificationCacheService
from apps.notifications.services.email_service import EmailService
from apps.notifications.services.sms_service import SMSService


class NotificationQueueService:
    @staticmethod
    @transaction.atomic
    def enfileirar(notificacao: Notificacao, prioridade: int = 5) -> FilaNotificacao:
        notificacao.estado = NotificacaoEstado.PENDENTE
        notificacao.save(update_fields=["estado", "updated_at"])
        return FilaNotificacao.objects.create(notificacao=notificacao, prioridade=prioridade)

    @staticmethod
    def processar_item(item: FilaNotificacao) -> FilaNotificacao:
        notificacao = item.notificacao
        notificacao.estado = NotificacaoEstado.PROCESSANDO
        notificacao.save(update_fields=["estado", "updated_at"])

        try:
            if notificacao.canal == "EMAIL" and notificacao.destinatario_email:
                EmailService.enviar(
                    destinatario=notificacao.destinatario_email,
                    assunto=notificacao.titulo,
                    corpo=notificacao.mensagem,
                    notificacao=notificacao,
                )
            elif notificacao.canal == "SMS" and notificacao.destinatario_telefone:
                SMSService.enviar(
                    telefone=notificacao.destinatario_telefone,
                    mensagem=notificacao.mensagem,
                    notificacao=notificacao,
                )
            else:
                notificacao.estado = NotificacaoEstado.ENTREGUE
                notificacao.save(update_fields=["estado", "updated_at"])

            item.processado_em = timezone.now()
            item.save(update_fields=["processado_em", "updated_at"])
        except Exception as exc:  # noqa: BLE001
            item.tentativas += 1
            item.erro = str(exc)
            notificacao.estado = NotificacaoEstado.FALHOU
            notificacao.save(update_fields=["estado", "updated_at"])
            item.save(update_fields=["tentativas", "erro", "updated_at"])

        if notificacao.utilizador_id:
            NotificationCacheService.invalidate_user(notificacao.utilizador_id)
        NotificationCacheService.invalidate_dashboard()
        return item

    @staticmethod
    def processar_pendentes(limite: int = 50) -> int:
        itens = (
            FilaNotificacao.objects.select_related("notificacao")
            .filter(processado_em__isnull=True, tentativas__lt=F("max_tentativas"))
            .order_by("prioridade", "created_at")[:limite]
        )
        processados = 0
        for item in itens:
            NotificationQueueService.processar_item(item)
            processados += 1
        return processados

    @staticmethod
    def reenviar_falhas(limite: int = 20) -> int:
        falhas = Notificacao.objects.filter(estado=NotificacaoEstado.FALHOU)[:limite]
        reenviados = 0
        for notificacao in falhas:
            notificacao.estado = NotificacaoEstado.PENDENTE
            notificacao.save(update_fields=["estado", "updated_at"])
            NotificationQueueService.enfileirar(notificacao, prioridade=1)
            reenviados += 1
        return reenviados
