"""Permissões do módulo médico."""

from apps.users.permissions import HasModulePermission

PRESCRIPTION_MAP = {
    "list": "doctors.prescription",
    "retrieve": "doctors.prescription",
    "create": "doctors.prescription",
    "partial_update": "doctors.prescription",
    "approve": "doctors.prescription",
    "finish": "doctors.prescription",
    "history": "doctors.prescription",
}

TREATMENT_MAP = {
    "list": "doctors.treatment",
    "retrieve": "doctors.treatment",
    "create": "doctors.treatment",
    "partial_update": "doctors.treatment",
    "finish": "doctors.treatment",
}

EVOLUTION_MAP = {
    "list": "doctors.evolution",
    "retrieve": "doctors.evolution",
    "create": "doctors.evolution",
    "partial_update": "doctors.evolution",
}

DISCHARGE_MAP = {
    "list": "doctors.discharge",
    "retrieve": "doctors.discharge",
    "create": "doctors.discharge",
    "partial_update": "doctors.discharge",
}

FOLLOWUP_MAP = {
    "list": "doctors.followup",
    "retrieve": "doctors.followup",
    "create": "doctors.followup",
}


class DoctorsPermissionMixin:
    permission_map: dict = PRESCRIPTION_MAP
    default_permission = "doctors.prescription"

    def get_permissions(self):
        return [HasModulePermission()]

    @property
    def required_permission(self) -> str:
        return self.permission_map.get(self.action, self.default_permission)
