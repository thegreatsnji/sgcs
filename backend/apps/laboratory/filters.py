"""Filtros do módulo de laboratório."""

import django_filters
from django.db.models import Q

from apps.appointments.constants import PedidoLaboratorioEstadoFaturacao
from apps.laboratory.models import PedidoLaboratorial


class PedidoLaboratorialFilter(django_filters.FilterSet):
    estado = django_filters.CharFilter(field_name="estado")
    prioridade = django_filters.CharFilter(field_name="prioridade")
    paciente = django_filters.NumberFilter(field_name="paciente_id")
    medico = django_filters.NumberFilter(field_name="medico_id")
    data_pedido = django_filters.DateFilter(field_name="data_pedido", lookup_expr="date")
    q = django_filters.CharFilter(method="filter_search")
    estado_faturacao = django_filters.CharFilter(method="filter_estado_faturacao")

    class Meta:
        model = PedidoLaboratorial
        fields = (
            "estado",
            "prioridade",
            "paciente",
            "medico",
            "data_pedido",
            "q",
            "estado_faturacao",
        )

    def filter_search(self, queryset, name, value):
        term = (value or "").strip()
        if not term:
            return queryset
        return queryset.filter(
            Q(numero_pedido__icontains=term)
            | Q(paciente__full_name__icontains=term)
            | Q(paciente__patient_number__icontains=term)
            | Q(exames__nome_exame__icontains=term)
        ).distinct()

    def filter_estado_faturacao(self, queryset, name, value):
        code = (value or "").strip()
        if not code:
            return queryset
        if code == PedidoLaboratorioEstadoFaturacao.NAO_APLICAVEL:
            return queryset.filter(
                Q(pedido_consulta__isnull=True)
                | Q(pedido_consulta__estado_faturacao=PedidoLaboratorioEstadoFaturacao.NAO_APLICAVEL)
            )
        return queryset.filter(pedido_consulta__estado_faturacao=code)
