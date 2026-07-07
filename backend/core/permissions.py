"""Permissões baseadas em perfis (RBAC)."""

from rest_framework.permissions import BasePermission

from core.constants import UserRole


class IsAdministrator(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == UserRole.ADMINISTRADOR
        )


class HasRole(BasePermission):
    allowed_roles: tuple[str, ...] = ()

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role in self.allowed_roles


class IsReceptionist(HasRole):
    allowed_roles = (UserRole.ADMINISTRADOR, UserRole.RECECIONISTA)


class IsDoctor(HasRole):
    allowed_roles = (UserRole.ADMINISTRADOR, UserRole.MEDICO)


class IsLaboratoryStaff(HasRole):
    allowed_roles = (UserRole.ADMINISTRADOR, UserRole.LABORATORIO)


class IsFinanceStaff(HasRole):
    allowed_roles = (UserRole.ADMINISTRADOR, UserRole.FINANCEIRO)
