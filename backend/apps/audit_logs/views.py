"""Views de auditoria."""

from rest_framework import generics

from apps.audit_logs.filters import AuditLogFilter
from apps.audit_logs.models import AuditLog
from apps.audit_logs.serializers import AuditLogSerializer
from apps.users.permissions import HasModulePermission
from core.pagination import StandardPagination
from core.responses import success_response


class AuditLogListView(generics.ListAPIView):
    queryset = AuditLog.objects.select_related("user").all()
    serializer_class = AuditLogSerializer
    pagination_class = StandardPagination
    filterset_class = AuditLogFilter
    ordering_fields = ["created_at", "action"]
    ordering = ["-created_at"]

    def get_permissions(self):
        return [HasModulePermission()]

    @property
    def required_permission(self):
        return "users.view"

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        paginated = self.get_paginated_response(serializer.data)
        return success_response(data=paginated.data)
