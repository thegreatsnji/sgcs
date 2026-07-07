"""Permissões do módulo de laboratório."""

from apps.users.permissions import HasModulePermission

LABORATORY_PERMISSION_MAP = {
    "list": "laboratory.view",
    "retrieve": "laboratory.view",
    "partial_update": "laboratory.edit",
    "update": "laboratory.edit",
    "pending": "laboratory.view",
    "today": "laboratory.view",
    "collection_queue": "laboratory.view",
    "receive": "laboratory.receive",
    "collect": "laboratory.collect",
    "start": "laboratory.process",
    "finish": "laboratory.finish",
}

LABORATORY_RESULT_PERMISSION_MAP = {
    "list": "laboratory.results.view",
    "retrieve": "laboratory.results.view",
    "create": "laboratory.results.create",
    "partial_update": "laboratory.results.edit",
    "update": "laboratory.results.edit",
    "validate_result": "laboratory.results.validate",
    "publish": "laboratory.results.publish",
    "attachments": "laboratory.results.create",
    "add_parameter": "laboratory.results.edit",
    "download": "laboratory.results.download",
}


class LaboratoryPermissionMixin:
    permission_map = LABORATORY_PERMISSION_MAP
    default_permission = "laboratory.view"

    def get_permissions(self):
        return [HasModulePermission()]

    @property
    def required_permission(self) -> str:
        return self.permission_map.get(self.action, self.default_permission)


class LaboratoryResultPermissionMixin:
    permission_map = LABORATORY_RESULT_PERMISSION_MAP
    default_permission = "laboratory.results.view"

    def get_permissions(self):
        return [HasModulePermission()]

    @property
    def required_permission(self) -> str:
        return self.permission_map.get(self.action, self.default_permission)
