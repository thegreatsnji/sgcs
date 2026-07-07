"""Permissões do módulo de notificações."""

NOTIFICATION_MAP = {
    "list": "notifications.view",
    "retrieve": "notifications.view",
    "create": "notifications.create",
    "partial_update": "notifications.edit",
    "destroy": "notifications.delete",
    "read": "notifications.view",
    "archive": "notifications.view",
    "unread": "notifications.view",
    "history": "notifications.history",
}

EMAIL_MAP = {
    "test": "notifications.send",
    "history": "notifications.history",
}

SMS_MAP = {
    "test": "notifications.send",
    "history": "notifications.history",
}

TEMPLATE_MAP = {
    "list": "notifications.template",
    "retrieve": "notifications.template",
    "create": "notifications.template",
    "partial_update": "notifications.template",
    "destroy": "notifications.template",
    "preview": "notifications.template",
}

PREFERENCE_MAP = {
    "list": "notifications.settings",
    "retrieve": "notifications.settings",
    "partial_update": "notifications.settings",
}


class NotificationsPermissionMixin:
    permission_map: dict = NOTIFICATION_MAP
    default_permission = "notifications.view"

    def get_permissions(self):
        from apps.users.permissions import HasModulePermission

        return [HasModulePermission()]

    @property
    def required_permission(self) -> str:
        return self.permission_map.get(self.action, self.default_permission)
