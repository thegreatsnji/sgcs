"""Filtros do módulo de pacientes."""

import django_filters
from django.db.models import Exists, OuterRef, Q

from apps.patients.models import Patient, PatientAllergy, PatientChronicDisease, PatientHistory


class PatientFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method="filter_search", label="Pesquisa")
    is_active = django_filters.BooleanFilter(field_name="is_active")
    is_deleted = django_filters.BooleanFilter(field_name="is_deleted")
    gender = django_filters.CharFilter(field_name="gender")
    document_type = django_filters.CharFilter(field_name="document_type")
    blood_type = django_filters.CharFilter(field_name="blood_type")
    birth_date_after = django_filters.DateFilter(field_name="birth_date", lookup_expr="gte")
    birth_date_before = django_filters.DateFilter(field_name="birth_date", lookup_expr="lte")
    created_after = django_filters.DateTimeFilter(field_name="created_at", lookup_expr="gte")
    created_before = django_filters.DateTimeFilter(field_name="created_at", lookup_expr="lte")
    has_allergies = django_filters.BooleanFilter(method="filter_has_allergies")
    has_chronic_diseases = django_filters.BooleanFilter(method="filter_has_chronic_diseases")

    class Meta:
        model = Patient
        fields = [
            "is_active",
            "is_deleted",
            "gender",
            "document_type",
            "blood_type",
        ]

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(full_name__icontains=value)
            | Q(first_name__icontains=value)
            | Q(last_name__icontains=value)
            | Q(document_number__icontains=value)
            | Q(phone__icontains=value)
            | Q(patient_number__icontains=value)
            | Q(email__icontains=value)
        )

    def filter_has_allergies(self, queryset, name, value):
        subquery = PatientAllergy.objects.filter(patient_id=OuterRef("pk"), is_active=True)
        if value:
            return queryset.filter(Exists(subquery))
        return queryset.filter(~Exists(subquery))

    def filter_has_chronic_diseases(self, queryset, name, value):
        subquery = PatientChronicDisease.objects.filter(patient_id=OuterRef("pk"), is_active=True)
        if value:
            return queryset.filter(Exists(subquery))
        return queryset.filter(~Exists(subquery))


class PatientHistoryFilter(django_filters.FilterSet):
    event_type = django_filters.CharFilter(field_name="event_type")
    source_module = django_filters.CharFilter(field_name="source_module")
    event_date_after = django_filters.DateTimeFilter(field_name="event_date", lookup_expr="gte")
    event_date_before = django_filters.DateTimeFilter(field_name="event_date", lookup_expr="lte")

    class Meta:
        model = PatientHistory
        fields = ["event_type", "source_module"]
