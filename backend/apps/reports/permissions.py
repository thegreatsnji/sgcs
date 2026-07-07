"""Permissões do módulo de relatórios."""

from apps.users.permissions import HasModulePermission


class ReportsPermissionMixin:
    view_permission = "reports.view"
    export_permission = "reports.export"

    def get_permissions(self):
        return [HasModulePermission()]

    @property
    def required_permission(self) -> str:
        export = getattr(self.request, "query_params", {}).get("export")
        if export:
            return self.export_permission
        return self.view_permission
