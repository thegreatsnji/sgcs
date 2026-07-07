"""Tarefas Celery do módulo de notificações."""

from config.celery import app


@app.task(name="notifications.enviar_email")
def enviar_email(historico_id: int | None = None, destinatario: str = "", assunto: str = "", corpo: str = "") -> dict:
    from apps.notifications.services.email_service import EmailService

    if historico_id:
        return {"status": "ok", "historico_id": historico_id}
    historico = EmailService.enviar(destinatario=destinatario, assunto=assunto, corpo=corpo)
    return {"status": "ok", "historico_id": historico.pk}


@app.task(name="notifications.enviar_sms")
def enviar_sms(telefone: str, mensagem: str) -> dict:
    from apps.notifications.services.sms_service import SMSService

    historico = SMSService.enviar(telefone=telefone, mensagem=mensagem)
    return {"status": "ok", "historico_id": historico.pk}


@app.task(name="notifications.processar_fila")
def processar_fila(limite: int = 50) -> dict:
    from apps.notifications.services.queue_service import NotificationQueueService

    processados = NotificationQueueService.processar_pendentes(limite=limite)
    return {"status": "ok", "processados": processados}


@app.task(name="notifications.reenviar_falhas")
def reenviar_falhas(limite: int = 20) -> dict:
    from apps.notifications.services.queue_service import NotificationQueueService

    reenviados = NotificationQueueService.reenviar_falhas(limite=limite)
    return {"status": "ok", "reenviados": reenviados}


@app.task(name="notifications.limpar_notificacoes_antigas")
def limpar_notificacoes_antigas(dias: int = 90) -> dict:
    from datetime import timedelta

    from django.utils import timezone

    from apps.notifications.models import Notificacao

    limite = timezone.now() - timedelta(days=dias)
    apagadas, _ = Notificacao.objects.filter(created_at__lt=limite, arquivada=True).delete()
    return {"status": "ok", "apagadas": apagadas}
