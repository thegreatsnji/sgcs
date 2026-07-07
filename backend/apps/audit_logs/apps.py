from django.apps import AppConfig


class AuditLogsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.audit_logs"
    label = "audit_logs"
    verbose_name = "Registos de Auditoria"

    def ready(self) -> None:
        # Importar signals na Sprint 3+
        # from . import signals  # noqa: F401
        pass
