"""Filtros do módulo de laboratório."""

import django_filters

from apps.laboratory.models import PedidoLaboratorial


class PedidoLaboratorialFilter(django_filters.FilterSet):
    estado = django_filters.CharFilter(field_name="estado")
    prioridade = django_filters.CharFilter(field_name="prioridade")
    paciente = django_filters.NumberFilter(field_name="paciente_id")
    medico = django_filters.NumberFilter(field_name="medico_id")
    data_pedido = django_filters.DateFilter(field_name="data_pedido", lookup_expr="date")

    class Meta:
        model = PedidoLaboratorial
        fields = ("estado", "prioridade", "paciente", "medico", "data_pedido")
