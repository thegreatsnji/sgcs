"""Serviço centralizado de auditoria."""

from apps.audit_logs.models import AuditAction, AuditLog


def get_client_info(request) -> tuple[str | None, str]:
    if request is None:
        return None, ""
    x_forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded:
        ip = x_forwarded.split(",")[0].strip()
    else:
        ip = request.META.get("REMOTE_ADDR")
    user_agent = request.META.get("HTTP_USER_AGENT", "")
    return ip, user_agent


class AuditService:
    @staticmethod
    def log(
        *,
        action: str,
        description: str,
        user=None,
        request=None,
        resource_type: str = "",
        resource_id: str = "",
        metadata: dict | None = None,
    ) -> AuditLog:
        ip_address, user_agent = get_client_info(request)
        return AuditLog.objects.create(
            user=user,
            action=action,
            ip_address=ip_address,
            user_agent=user_agent,
            description=description,
            resource_type=resource_type,
            resource_id=str(resource_id) if resource_id else "",
            metadata=metadata or {},
        )

    @staticmethod
    def log_login(user, request=None):
        return AuditService.log(
            action=AuditAction.LOGIN,
            user=user,
            request=request,
            description=f"Login realizado por {user.email}.",
            resource_type="user",
            resource_id=user.pk,
        )

    @staticmethod
    def log_logout(user, request=None):
        return AuditService.log(
            action=AuditAction.LOGOUT,
            user=user,
            request=request,
            description=f"Logout realizado por {user.email}.",
            resource_type="user",
            resource_id=user.pk,
        )
