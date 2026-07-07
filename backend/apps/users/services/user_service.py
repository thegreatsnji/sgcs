"""Serviços de gestão de utilizadores."""

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from apps.audit_logs.models import AuditAction
from apps.audit_logs.services import AuditService
from apps.authentication.models import UserRole
from apps.users.models import UserSession

User = get_user_model()


class UserService:
    @staticmethod
    def get_active_admin_count() -> int:
        return User.objects.filter(
            role=UserRole.ADMINISTRADOR,
            is_active=True,
            deleted_at__isnull=True,
        ).count()

    @staticmethod
    def validate_can_delete(actor, target) -> None:
        if actor.pk == target.pk:
            raise ValueError("Não pode eliminar o próprio utilizador.")
        if (
            target.role == UserRole.ADMINISTRADOR
            and UserService.get_active_admin_count() <= 1
        ):
            raise ValueError("Não é possível eliminar o último administrador.")

    @staticmethod
    def validate_can_deactivate(actor, target) -> None:
        if actor.pk == target.pk:
            raise ValueError("Não pode desativar o próprio utilizador.")
        if (
            target.role == UserRole.ADMINISTRADOR
            and target.is_active
            and UserService.get_active_admin_count() <= 1
        ):
            raise ValueError("Não é possível desativar o último administrador.")

    @staticmethod
    @transaction.atomic
    def soft_delete_user(actor, user, request=None) -> User:
        UserService.validate_can_delete(actor, user)
        user.soft_delete()
        UserSession.objects.filter(user=user, is_active=True).update(
            is_active=False,
            logged_out_at=timezone.now(),
        )
        AuditService.log(
            action=AuditAction.USER_DELETE,
            user=actor,
            request=request,
            description=f"Utilizador {user.email} eliminado (soft delete).",
            resource_type="user",
            resource_id=user.pk,
        )
        return user

    @staticmethod
    def activate_user(actor, user, request=None) -> User:
        user.is_active = True
        user.deleted_at = None
        user.save(update_fields=["is_active", "deleted_at"])
        AuditService.log(
            action=AuditAction.USER_ACTIVATE,
            user=actor,
            request=request,
            description=f"Utilizador {user.email} ativado.",
            resource_type="user",
            resource_id=user.pk,
        )
        return user

    @staticmethod
    def deactivate_user(actor, user, request=None) -> User:
        UserService.validate_can_deactivate(actor, user)
        user.is_active = False
        user.save(update_fields=["is_active"])
        UserSession.objects.filter(user=user, is_active=True).update(
            is_active=False,
            logged_out_at=timezone.now(),
        )
        AuditService.log(
            action=AuditAction.USER_DEACTIVATE,
            user=actor,
            request=request,
            description=f"Utilizador {user.email} desativado.",
            resource_type="user",
            resource_id=user.pk,
        )
        return user

    @staticmethod
    def create_session(user, request=None, refresh_jti: str = "") -> UserSession:
        from apps.audit_logs.services import get_client_info

        ip_address, user_agent = get_client_info(request)
        return UserSession.objects.create(
            user=user,
            refresh_jti=refresh_jti,
            ip_address=ip_address,
            user_agent=user_agent,
        )

    @staticmethod
    def touch_activity(user):
        user.last_activity = timezone.now()
        user.save(update_fields=["last_activity"])
