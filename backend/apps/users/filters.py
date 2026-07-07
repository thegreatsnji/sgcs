"""Filtros de pesquisa de utilizadores."""

import django_filters
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()


class UserFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method="filter_search", label="Pesquisa")
    role = django_filters.CharFilter(field_name="role")
    is_active = django_filters.BooleanFilter(field_name="is_active")
    date_joined_after = django_filters.DateFilter(field_name="date_joined", lookup_expr="gte")
    date_joined_before = django_filters.DateFilter(field_name="date_joined", lookup_expr="lte")
    last_login_after = django_filters.DateFilter(field_name="last_login", lookup_expr="gte")
    last_login_before = django_filters.DateFilter(field_name="last_login", lookup_expr="lte")

    class Meta:
        model = User
        fields = ["role", "is_active"]

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(first_name__icontains=value)
            | Q(last_name__icontains=value)
            | Q(email__icontains=value)
            | Q(phone__icontains=value)
        )
