"""Filtros de resultados laboratoriais."""

import django_filters

from apps.laboratory.models import ResultadoLaboratorial


class ResultadoLaboratorialFilter(django_filters.FilterSet):
    estado = django_filters.CharFilter(field_name="estado")
    paciente = django_filters.NumberFilter(field_name="pedido_laboratorial__paciente_id")
    pedido = django_filters.NumberFilter(field_name="pedido_laboratorial_id")

    class Meta:
        model = ResultadoLaboratorial
        fields = ("estado", "paciente", "pedido")
