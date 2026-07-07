"""Filtros do módulo de receção."""

import django_filters

from apps.reception.models import ReceptionCheckIn, WaitingQueue


class WaitingQueueFilter(django_filters.FilterSet):
    status = django_filters.CharFilter(field_name="status")
    priority = django_filters.CharFilter(field_name="check_in__priority")
    patient = django_filters.NumberFilter(field_name="patient_id")

    class Meta:
        model = WaitingQueue
        fields = ["status", "patient"]


class ReceptionHistoryFilter(django_filters.FilterSet):
    patient = django_filters.NumberFilter(field_name="patient_id")
    status = django_filters.CharFilter(field_name="status")
    priority = django_filters.CharFilter(field_name="priority")
    check_in_after = django_filters.DateTimeFilter(field_name="check_in_time", lookup_expr="gte")
    check_in_before = django_filters.DateTimeFilter(field_name="check_in_time", lookup_expr="lte")

    class Meta:
        model = ReceptionCheckIn
        fields = ["status", "priority", "patient"]
