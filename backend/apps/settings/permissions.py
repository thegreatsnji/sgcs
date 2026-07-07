"""Permissões do módulo de configurações."""

from apps.users.permissions import HasModulePermission

SPECIALTY_MAP = {
    "list": "settings.view",
    "retrieve": "settings.view",
    "create": "settings.edit",
    "partial_update": "settings.edit",
    "destroy": "settings.delete",
}

DEPARTMENT_MAP = SPECIALTY_MAP
ROOM_MAP = SPECIALTY_MAP
HOLIDAY_MAP = SPECIALTY_MAP
CONSULTATION_TYPE_MAP = SPECIALTY_MAP
LAB_EXAM_MAP = SPECIALTY_MAP
WORKING_HOURS_MAP = SPECIALTY_MAP
BACKUP_MAP = {
    "list": "settings.backup",
    "retrieve": "settings.backup",
    "create": "settings.backup",
    "restore": "settings.backup",
}


class SettingsPermissionMixin:
    permission_map: dict = SPECIALTY_MAP
    default_permission = "settings.view"

    def get_permissions(self):
        return [HasModulePermission()]

    @property
    def required_permission(self) -> str:
        return self.permission_map.get(self.action, self.default_permission)
