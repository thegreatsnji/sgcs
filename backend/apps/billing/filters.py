"""Filtros do módulo de faturação."""

import django_filters
from django.db.models import Q

from apps.billing.models import Fatura, Orcamento, Pagamento, Recibo, Servico


class ServicoFilter(django_filters.FilterSet):
    categoria = django_filters.CharFilter()
    activo = django_filters.BooleanFilter()
    search = django_filters.CharFilter(method="filter_search")

    class Meta:
        model = Servico
        fields = ["categoria", "activo"]

    def filter_search(self, queryset, name, value):
        return queryset.filter(Q(nome__icontains=value) | Q(codigo__icontains=value))


class OrcamentoFilter(django_filters.FilterSet):
    paciente = django_filters.NumberFilter(field_name="paciente_id")
    estado = django_filters.CharFilter()

    class Meta:
        model = Orcamento
        fields = ["paciente", "estado"]


class FaturaFilter(django_filters.FilterSet):
    paciente = django_filters.NumberFilter(field_name="paciente_id")
    consulta = django_filters.NumberFilter(field_name="consulta_id")
    estado = django_filters.CharFilter()

    class Meta:
        model = Fatura
        fields = ["paciente", "consulta", "estado"]


class PagamentoFilter(django_filters.FilterSet):
    fatura = django_filters.NumberFilter(field_name="fatura_id")
    estado = django_filters.CharFilter()

    class Meta:
        model = Pagamento
        fields = ["fatura", "estado"]


class ReciboFilter(django_filters.FilterSet):
    class Meta:
        model = Recibo
        fields = []
