from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.notifications"
    label = "notifications"
    verbose_name = "Notificações"

    def ready(self) -> None:
        from apps.notifications.event_handlers import register_notification_handlers

        register_notification_handlers()
