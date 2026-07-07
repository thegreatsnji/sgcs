"""Geração de números de pedido laboratorial."""

from django.utils import timezone

from apps.laboratory.constants import ORDER_NUMBER_PREFIX
from apps.laboratory.models import PedidoLaboratorial


class LaboratoryNumberService:
    @staticmethod
    def generate() -> str:
        year = timezone.now().year
        prefix = f"{ORDER_NUMBER_PREFIX}-{year}-"
        last = (
            PedidoLaboratorial.objects.filter(numero_pedido__startswith=prefix)
            .order_by("-numero_pedido")
            .values_list("numero_pedido", flat=True)
            .first()
        )
        if last:
            try:
                sequence = int(last.split("-")[-1]) + 1
            except ValueError:
                sequence = 1
        else:
            sequence = 1
        return f"{prefix}{sequence:05d}"
