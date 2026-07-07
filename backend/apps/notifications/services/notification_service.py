"""Serviço principal de notificações."""

from django.db import transaction
from django.utils import timezone

from apps.audit_logs.models import AuditAction
from apps.audit_logs.services import AuditService
from apps.authentication.models import User, UserRole
from apps.notifications.constants import NotificacaoCanal, NotificacaoEstado, NotificacaoTipo
from apps.notifications.models import Notificacao
from apps.notifications.services.cache_service import NotificationCacheService
from apps.notifications.services.preference_service import NotificationPreferenceService
from apps.notifications.services.queue_service import NotificationQueueService


class NotificationService:
    @staticmethod
    def _log(action, user, request, notificacao, description, metadata=None):
        AuditService.log(
            action=action,
            user=user,
            request=request,
            description=description,
            resource_type="notificacao",
            resource_id=str(notificacao.pk),
            metadata=metadata or {},
        )

    @staticmethod
    @transaction.atomic
    def criar(
        *,
        titulo: str,
        mensagem: str,
        utilizador: User | None = None,
        tipo: str = NotificacaoTipo.INFORMATIVA,
        canal: str = NotificacaoCanal.INTERNO,
        evento_origem: str = "",
        metadados: dict | None = None,
        destinatario_email: str = "",
        destinatario_telefone: str = "",
        criador: User | None = None,
        request=None,
        enfileirar: bool = True,
    ) -> Notificacao | None:
        if utilizador and not NotificationPreferenceService.pode_receber(
            utilizador, canal=canal, tipo=tipo
        ):
            return None

        notificacao = Notificacao.objects.create(
            utilizador=utilizador,
            titulo=titulo,
            mensagem=mensagem,
            tipo=tipo,
            canal=canal,
            estado=NotificacaoEstado.PENDENTE if canal != NotificacaoCanal.INTERNO else NotificacaoEstado.ENTREGUE,
            evento_origem=evento_origem,
            metadados=metadados or {},
            destinatario_email=destinatario_email or (utilizador.email if utilizador else ""),
            destinatario_telefone=destinatario_telefone,
        )
        NotificationService._log(
            AuditAction.NOTIFICACAO_CRIADA,
            criador,
            request,
            notificacao,
            f"Notificação '{titulo}' criada.",
        )
        if canal != NotificacaoCanal.INTERNO and enfileirar:
            NotificationQueueService.enfileirar(notificacao)
        else:
            NotificationService._log(
                AuditAction.NOTIFICACAO_ENVIADA,
                criador,
                request,
                notificacao,
                "Notificação interna entregue.",
            )
        if utilizador:
            NotificationCacheService.invalidate_user(utilizador.pk)
        NotificationCacheService.invalidate_dashboard()
        return notificacao

    @staticmethod
    def marcar_lida(notificacao_id: int, user: User, request=None) -> Notificacao:
        notificacao = Notificacao.objects.get(pk=notificacao_id, utilizador=user)
        notificacao.lida = True
        notificacao.lida_em = timezone.now()
        notificacao.estado = NotificacaoEstado.LIDA
        notificacao.save(update_fields=["lida", "lida_em", "estado", "updated_at"])
        NotificationService._log(
            AuditAction.NOTIFICACAO_LIDA,
            user,
            request,
            notificacao,
            "Notificação marcada como lida.",
        )
        NotificationCacheService.invalidate_user(user.pk)
        return notificacao

    @staticmethod
    def arquivar(notificacao_id: int, user: User) -> Notificacao:
        notificacao = Notificacao.objects.get(pk=notificacao_id, utilizador=user)
        notificacao.arquivada = True
        notificacao.save(update_fields=["arquivada", "updated_at"])
        NotificationCacheService.invalidate_user(user.pk)
        return notificacao

    @staticmethod
    def listar_nao_lidas(user: User) -> list[dict]:
        cached = NotificationCacheService.get_nao_lidas(user.pk)
        if cached is not None:
            return cached
        qs = (
            Notificacao.objects.filter(utilizador=user, lida=False, arquivada=False)
            .order_by("-created_at")[:20]
            .values("id", "titulo", "mensagem", "tipo", "canal", "estado", "created_at")
        )
        data = list(qs)
        NotificationCacheService.set_nao_lidas(user.pk, data)
        return data

    @staticmethod
    def contador_nao_lidas(user: User) -> int:
        cached = NotificationCacheService.get_contador(user.pk)
        if cached is not None:
            return cached
        count = Notificacao.objects.filter(utilizador=user, lida=False, arquivada=False).count()
        NotificationCacheService.set_contador(user.pk, count)
        return count

    @staticmethod
    def historico(user: User, limite: int = 50) -> list[dict]:
        return list(
            Notificacao.objects.filter(utilizador=user)
            .order_by("-created_at")[:limite]
            .values("id", "titulo", "tipo", "canal", "estado", "lida", "arquivada", "created_at")
        )

    @staticmethod
    def dashboard_kpis() -> dict:
        cached = NotificationCacheService.get_dashboard()
        if cached:
            return cached
        hoje = timezone.localdate()
        data = {
            "total": Notificacao.objects.count(),
            "nao_lidas": Notificacao.objects.filter(lida=False, arquivada=False).count(),
            "emails_hoje": __import__("apps.notifications.models", fromlist=["HistoricoEmail"])
            .HistoricoEmail.objects.filter(enviado_em__date=hoje)
            .count(),
            "sms_hoje": __import__("apps.notifications.models", fromlist=["HistoricoSMS"])
            .HistoricoSMS.objects.filter(enviado_em__date=hoje)
            .count(),
            "falhas": Notificacao.objects.filter(estado=NotificacaoEstado.FALHOU).count(),
            "fila_pendente": __import__("apps.notifications.models", fromlist=["FilaNotificacao"])
            .FilaNotificacao.objects.filter(processado_em__isnull=True)
            .count(),
        }
        NotificationCacheService.set_dashboard(data)
        return data

    @staticmethod
    def notificar_administradores(titulo: str, mensagem: str, evento: str, tipo: str = NotificacaoTipo.AVISO):
        admins = User.objects.filter(role=UserRole.ADMINISTRADOR, is_active=True)
        for admin in admins:
            if NotificationPreferenceService.obter_ou_criar(admin).receber_alertas_admin:
                NotificationService.criar(
                    titulo=titulo,
                    mensagem=mensagem,
                    utilizador=admin,
                    tipo=tipo,
                    canal=NotificacaoCanal.INTERNO,
                    evento_origem=evento,
                )
