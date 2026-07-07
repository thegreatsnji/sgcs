"""Serviços de RBAC."""

from apps.authentication.models import UserRole
from apps.users.models import ModulePermission, Role, UserGroup


class RBACService:
    @staticmethod
    def get_user_permissions(user) -> set[str]:
        if not user or not user.is_authenticated:
            return set()

        if user.is_superuser or user.role == UserRole.ADMINISTRADOR:
            return set(ModulePermission.objects.values_list("codename", flat=True))

        permissions: set[str] = set()

        role = Role.objects.filter(slug=user.role).prefetch_related("permissions").first()
        if role:
            permissions.update(role.permissions.values_list("codename", flat=True))

        group_permissions = ModulePermission.objects.filter(
            groups__members=user,
            groups__is_active=True,
        ).values_list("codename", flat=True)
        permissions.update(group_permissions)

        return permissions

    @staticmethod
    def user_has_permission(user, codename: str) -> bool:
        return codename in RBACService.get_user_permissions(user)

    @staticmethod
    def user_has_any_permission(user, codenames: list[str]) -> bool:
        user_permissions = RBACService.get_user_permissions(user)
        return any(code in user_permissions for code in codenames)

    @staticmethod
    def can_manage_role(actor, target_role: str) -> bool:
        if actor.is_superuser or actor.role == UserRole.ADMINISTRADOR:
            return True
        actor_permissions = RBACService.get_user_permissions(actor)
        return "users.admin" in actor_permissions and target_role != UserRole.ADMINISTRADOR
