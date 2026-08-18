"""Permissões do módulo de pacientes."""

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

    @property
    def required_permission(self) -> str:
        if self.action in ("list", "retrieve"):
            return "patients.view"
        if self.action in self.nested_write_actions:
            if self.action == "create":
                if getattr(self, "basename", "") in CLINICAL_NESTED_BASENAMES:
                    return "patients.edit"
                return "patients.create"
            return "patients.edit"
        return self.permission_map.get(self.action, self.default_permission)
