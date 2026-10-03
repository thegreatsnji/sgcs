from rest_framework.permissions import BasePermission

from apps.users.services.rbac_service import RBACService

VIEW_CODES = ("stock.view", "pharmacy.view")
CREATE_CODES = ("stock.create", "pharmacy.create")
EDIT_CODES = ("stock.edit", "pharmacy.edit")
ENTRY_CODES = ("stock.entry", "stock.edit", "pharmacy.edit")
EXIT_CODES = ("stock.exit", "stock.edit", "pharmacy.edit")
ADJUST_CODES = ("stock.adjust", "stock.edit", "pharmacy.edit")
HISTORY_CODES = ("stock.history", "stock.view", "pharmacy.view")


def has_any(user, codes: tuple[str, ...]) -> bool:
    return RBACService.user_has_any_permission(user, list(codes))


class _AnyPermission(BasePermission):
    codes: tuple[str, ...] = ()

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        return has_any(user, self.codes)


def require_any(*codenames: str):
    captured = tuple(codenames)

    class _P(_AnyPermission):
        codes = captured

    return _P
