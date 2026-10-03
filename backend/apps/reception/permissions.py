"""Permissões do módulo de receção."""

from apps.users.permissions import HasModulePermission

RECEPTION_PERMISSION_MAP = {
    "check_in": "reception.create",
    "queue": "reception.view",
    "update_queue": "reception.edit",
    "assign_to_doctor": "reception.edit",
    "doctor_assignment_options": "reception.view",
    "history": "reception.view",
    "create_referral": "reception.edit",
}


class ReceptionPermissionMixin:
    permission_map = RECEPTION_PERMISSION_MAP
    default_permission = "reception.view"

    def get_permissions(self):
        return [HasModulePermission()]

    @property
    def required_permission(self) -> str:
        return self.permission_map.get(self.action, self.default_permission)
