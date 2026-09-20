"""Permissões do módulo de faturação."""

from apps.users.permissions import HasModulePermission

SERVICE_PERMISSION_MAP = {
    "list": "billing.view",
    "retrieve": "billing.view",
    "create": "billing.delete",
    "partial_update": "billing.delete",
    "update": "billing.delete",
    "destroy": "billing.delete",
}

QUOTE_PERMISSION_MAP = {
    "list": "billing.view",
    "retrieve": "billing.view",
    "create": "billing.quote",
    "partial_update": "billing.edit",
    "update": "billing.edit",
    "approve": "billing.quote",
    "add_item": "billing.edit",
}

INVOICE_PERMISSION_MAP = {
    "list": "billing.view",
    "retrieve": "billing.view",
    "create": "billing.create",
    "partial_update": "billing.edit",
    "update": "billing.edit",
    "cancel": "billing.edit",
    "add_item": "billing.edit",
    # Autorizações de redução (ViewSet partilha este mixin)
    "aprovar": "billing.view",
    "rejeitar": "billing.view",
}

PAYMENT_PERMISSION_MAP = {
    "list": "billing.view",
    "retrieve": "billing.view",
    "create": "billing.payment",
    "partial_update": "billing.payment",
    "update": "billing.payment",
    "confirm": "billing.payment",
}

RECEIPT_PERMISSION_MAP = {
    "list": "billing.receipt",
    "retrieve": "billing.receipt",
}


class BillingPermissionMixin:
    permission_map: dict = SERVICE_PERMISSION_MAP
    default_permission = "billing.view"

    def get_permissions(self):
        return [HasModulePermission()]

    @property
    def required_permission(self) -> str:
        return self.permission_map.get(self.action, self.default_permission)


class ServicePermissionMixin(BillingPermissionMixin):
    permission_map = SERVICE_PERMISSION_MAP


class QuotePermissionMixin(BillingPermissionMixin):
    permission_map = QUOTE_PERMISSION_MAP


class InvoicePermissionMixin(BillingPermissionMixin):
    permission_map = INVOICE_PERMISSION_MAP


class PaymentPermissionMixin(BillingPermissionMixin):
    permission_map = PAYMENT_PERMISSION_MAP


class ReceiptPermissionMixin(BillingPermissionMixin):
    permission_map = RECEIPT_PERMISSION_MAP
