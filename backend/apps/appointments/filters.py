"""Filtros do módulo de consultas."""

import django_filters

from apps.appointments.models import Appointment


class AppointmentFilter(django_filters.FilterSet):
    patient = django_filters.NumberFilter(field_name="patient_id")
    doctor = django_filters.NumberFilter(field_name="doctor_id")
    status = django_filters.CharFilter(field_name="status")
    priority = django_filters.CharFilter(field_name="priority")
    consultation_date = django_filters.DateFilter(field_name="consultation_date")
    scheduled_after = django_filters.DateTimeFilter(field_name="scheduled_at", lookup_expr="gte")
    scheduled_before = django_filters.DateTimeFilter(field_name="scheduled_at", lookup_expr="lte")

    class Meta:
        model = Appointment
        fields = ["patient", "doctor", "status", "priority", "consultation_date"]
