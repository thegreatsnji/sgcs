"""Permissões RBAC do módulo de utilizadores."""

from rest_framework.permissions import BasePermission

from apps.authentication.models import UserRole
from apps.users.services.rbac_service import RBACService


class HasModulePermission(BasePermission):
    permission_codename: str = ""

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        if user.is_superuser or user.role == UserRole.ADMINISTRADOR:
            return True

        codename = getattr(view, "required_permission", None) or self.permission_codename
        if not codename:
            return False

        return RBACService.user_has_permission(user, codename)


def require_permission(codename: str):
    class _Permission(HasModulePermission):
        permission_codename = codename

    return _Permission
