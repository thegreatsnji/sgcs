"""Serviço de backups (estrutura preparada)."""

from django.utils import timezone

from apps.audit_logs.models import AuditAction
from apps.audit_logs.services import AuditService
from apps.settings.models import BackupRegisto
from core.events.event_bus import event_bus
from core.events.events import EventNames


class BackupService:
    @staticmethod
    def criar_backup(tipo: str, user=None, request=None) -> BackupRegisto:
        backup = BackupRegisto.objects.create(
            tipo=tipo,
            estado=BackupRegisto.ESTADO_CONCLUIDO,
            ficheiro=f"backup_{timezone.now().strftime('%Y%m%d_%H%M%S')}.sql",
            tamanho_bytes=0,
            criado_por=user,
            observacoes="Backup simulado (stub Celery).",
        )
        AuditService.log(
            action=AuditAction.BACKUP_CREATED,
            user=user,
            request=request,
            description=f"Backup {tipo} criado.",
            resource_type="backup",
            resource_id=str(backup.pk),
        )
        event_bus.publish(EventNames.BACKUP_CREATED, {"backup_id": backup.pk, "tipo": tipo})
        from apps.settings.tasks import backup_database

        backup_database.delay(backup.pk)
        return backup

    @staticmethod
    def restaurar_backup(backup_id: int, user=None, request=None) -> BackupRegisto:
        backup = BackupRegisto.objects.get(pk=backup_id)
        AuditService.log(
            action=AuditAction.BACKUP_RESTORED,
            user=user,
            request=request,
            description=f"Restauro do backup #{backup_id} iniciado.",
            resource_type="backup",
            resource_id=str(backup_id),
        )
        event_bus.publish(EventNames.BACKUP_RESTORED, {"backup_id": backup_id})
        from apps.settings.tasks import restore_database

        restore_database.delay(backup_id)
        return backup

    @staticmethod
    def listar_backups():
        return BackupRegisto.objects.all()
