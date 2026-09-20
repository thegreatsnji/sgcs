"""Permissões do módulo de pacientes."""

from rest_framework.permissions import BasePermission

from apps.patients.privacy import user_can_access_clinical_content
from apps.users.permissions import HasModulePermission

PATIENT_PERMISSION_MAP = {
    "list": "patients.view",
    "retrieve": "patients.view",
    "create": "patients.create",
    "update": "patients.edit",
    "partial_update": "patients.edit",
    "destroy": "patients.delete",
    "activate": "patients.edit",
    "deactivate": "patients.delete",
    "check_duplicate": "patients.create",
    "export": "patients.export",
    "print": "patients.print",
    "audit_trail": "patients.view",
    "appointments": "patients.view",
    "lab_orders": "patients.view",
    "prescriptions": "patients.view",
    "payments": "patients.view",
    "balance": "patients.view",
    "set_primary": "patients.edit",
    "pin": "patients.edit",
    "unpin": "patients.edit",
    "confirm_imported_data": "patients.edit",
}

CLINICAL_NESTED_BASENAMES = {
    "patient-allergy",
    "patient-chronic-disease",
    "patient-observation",
}


class HasPatientClinicalWritePermission(BasePermission):
    """Escrita de alergias / crónicas / observações — só equipa clínica."""

    message = "Não tem permissão para alterar dados clínicos do utente."

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        return user_can_access_clinical_content(user)


class PatientPermissionMixin:
    permission_map = PATIENT_PERMISSION_MAP
    default_permission = "patients.view"

    def get_permissions(self):
        return [HasModulePermission()]

    @property
    def required_permission(self) -> str:
        return self.permission_map.get(self.action, self.default_permission)


class NestedPatientPermissionMixin(PatientPermissionMixin):
    nested_write_actions = {"create", "update", "partial_update", "destroy", "set_primary", "pin", "unpin"}

    def get_permissions(self):
        basename = getattr(self, "basename", "")
        if (
            basename in CLINICAL_NESTED_BASENAMES
            and self.action in self.nested_write_actions
        ):
            return [HasPatientClinicalWritePermission()]
        return [HasModulePermission()]

    @property
    def required_permission(self) -> str:
        if self.action in ("list", "retrieve"):
            return "patients.view"
        if self.action in self.nested_write_actions:
            if self.action == "create":
                if getattr(self, "basename", "") in CLINICAL_NESTED_BASENAMES:
                    # Codename só para HasModulePermission fallback; escrita clínica usa HasPatientClinicalWritePermission.
                    return "appointments.clinical"
                return "patients.create"
            if getattr(self, "basename", "") in CLINICAL_NESTED_BASENAMES:
                return "appointments.clinical"
            return "patients.edit"
        return self.permission_map.get(self.action, self.default_permission)
