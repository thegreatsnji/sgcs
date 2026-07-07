"""Validadores do módulo de utilizadores."""

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from apps.authentication.models import UserRole
from apps.users.services.rbac_service import RBACService

User = get_user_model()


def validate_role_assignment(actor, role: str) -> None:
    if role == UserRole.ADMINISTRADOR and actor.role != UserRole.ADMINISTRADOR:
        if not RBACService.user_has_permission(actor, "users.admin"):
            raise ValidationError("Sem permissão para atribuir perfil de Administrador.")


def validate_password_change(user, old_password: str, new_password: str) -> None:
    if not user.check_password(old_password):
        raise ValidationError("Palavra-passe atual incorreta.")
    if old_password == new_password:
        raise ValidationError("A nova palavra-passe deve ser diferente da atual.")
