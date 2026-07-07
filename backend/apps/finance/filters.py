"""Filtros do módulo financeiro."""

import django_filters

from apps.finance.models import Caixa, Despesa, MovimentoFinanceiro


class CaixaFilter(django_filters.FilterSet):
    estado = django_filters.CharFilter()

    class Meta:
        model = Caixa
        fields = ["estado"]


class MovimentoFilter(django_filters.FilterSet):
    caixa = django_filters.NumberFilter(field_name="caixa_id")
    tipo = django_filters.CharFilter()

    class Meta:
        model = MovimentoFinanceiro
        fields = ["caixa", "tipo"]


class DespesaFilter(django_filters.FilterSet):
    estado = django_filters.CharFilter()
    categoria = django_filters.CharFilter()

    class Meta:
        model = Despesa
        fields = ["estado", "categoria"]
