"""Permissões do módulo financeiro."""

from apps.users.permissions import HasModulePermission

CASH_REGISTER_MAP = {
    "list": "finance.view",
    "retrieve": "finance.view",
    "create": "finance.create",
    "partial_update": "finance.edit",
    "open": "finance.cash",
    "close": "finance.cash",
    "history": "finance.view",
}

MOVEMENT_MAP = {
    "list": "finance.view",
    "retrieve": "finance.view",
    "create": "finance.create",
}

EXPENSE_MAP = {
    "list": "finance.view",
    "retrieve": "finance.view",
    "create": "finance.expense",
    "partial_update": "finance.edit",
    "destroy": "finance.delete",
    "approve": "finance.expense",
    "pay": "finance.expense",
    "cancel": "finance.edit",
}

CATEGORY_MAP = {
    "list": "finance.view",
    "retrieve": "finance.view",
    "create": "finance.create",
    "partial_update": "finance.edit",
    "destroy": "finance.delete",
}

REPORT_MAP = {
    "daily": "finance.report",
    "monthly": "finance.report",
    "yearly": "finance.report",
}


class FinancePermissionMixin:
    permission_map: dict = CASH_REGISTER_MAP
    default_permission = "finance.view"

    def get_permissions(self):
        return [HasModulePermission()]

    @property
    def required_permission(self) -> str:
        return self.permission_map.get(self.action, self.default_permission)
