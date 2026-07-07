"""Permissões do módulo de consultas."""

from apps.authentication.models import UserRole
from apps.users.permissions import HasModulePermission
from apps.users.services.rbac_service import RBACService

APPOINTMENT_PERMISSION_MAP = {
    "list": "appointments.view",
    "retrieve": "appointments.view",
    "create": "appointments.create",
    "update": "appointments.edit",
    "partial_update": "appointments.edit",
    "destroy": "appointments.delete",
    "queue": "appointments.view",
    "today": "appointments.view",
    "doctor": "appointments.view",
    "calendar": "appointments.view",
    "confirm": "appointments.confirm",
    "start": "appointments.start",
    "complete": "appointments.finish",
    "finish": "appointments.finish",
    "cancel": "appointments.cancel",
    "clinical_record": "appointments.view",
    "clinical_record": "appointments.clinical",
    "vital_signs": "appointments.clinical",
    "diagnoses": "appointments.diagnosis",
    "laboratory": "appointments.request_lab",
    "imaging": "appointments.request_imaging",
    "follow_up": "appointments.followup",
}

# Compatibilidade: PATCH clinical aceita também appointments.edit
CLINICAL_PERMISSION_FALLBACKS = {
    "clinical_record": ["appointments.edit"],
}


class HasAppointmentPermission(HasModulePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser or user.role == UserRole.ADMINISTRADOR:
            return True

        codename = getattr(view, "required_permission", None) or self.permission_codename
        if not codename:
            return False
        if RBACService.user_has_permission(user, codename):
            return True

        fallbacks = CLINICAL_PERMISSION_FALLBACKS.get(getattr(view, "action", ""), [])
        return RBACService.user_has_any_permission(user, fallbacks)


class AppointmentPermissionMixin:
    permission_map = APPOINTMENT_PERMISSION_MAP
    default_permission = "appointments.view"

    def get_permissions(self):
        return [HasAppointmentPermission()]

    @property
    def required_permission(self) -> str:
        return self.permission_map.get(self.action, self.default_permission)
