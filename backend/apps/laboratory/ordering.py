"""Ordenação clínica de pedidos laboratoriais."""

from django.db.models import Case, IntegerField, When

from apps.reception.constants import PRIORITY_ORDER, QueuePriority


def priority_order_case(*, field: str = "prioridade"):
    """Case/When para ordenar prioridade por significado clínico (não alfabético)."""
    whens = [When(**{field: priority.value}, then=rank) for priority, rank in PRIORITY_ORDER.items()]
    return Case(*whens, default=99, output_field=IntegerField())
