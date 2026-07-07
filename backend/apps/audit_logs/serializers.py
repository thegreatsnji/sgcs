"""Serializers de auditoria."""

from rest_framework import serializers

from apps.audit_logs.models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True, default=None)
    user_name = serializers.CharField(source="user.get_full_name", read_only=True, default=None)

    class Meta:
        model = AuditLog
        fields = (
            "id",
            "user",
            "user_email",
            "user_name",
            "action",
            "ip_address",
            "user_agent",
            "description",
            "resource_type",
            "resource_id",
            "metadata",
            "created_at",
        )
