"""Filtros de auditoria."""

import django_filters

from apps.audit_logs.models import AuditLog


class AuditLogFilter(django_filters.FilterSet):
    action = django_filters.CharFilter(field_name="action")
    user = django_filters.NumberFilter(field_name="user_id")
    resource_type = django_filters.CharFilter(field_name="resource_type")
    resource_id = django_filters.CharFilter(field_name="resource_id")
    created_after = django_filters.DateTimeFilter(field_name="created_at", lookup_expr="gte")
    created_before = django_filters.DateTimeFilter(field_name="created_at", lookup_expr="lte")
    search = django_filters.CharFilter(field_name="description", lookup_expr="icontains")

    class Meta:
        model = AuditLog
        fields = ["action", "user", "resource_type", "resource_id"]
