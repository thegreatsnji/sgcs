from django.db import transaction

from apps.pharmacy.constants import TipoMovimentoStockUrgencia
from apps.pharmacy.models import MedicamentoUrgencia, MovimentoStockUrgencia


class StockUrgenciaError(Exception):
    pass


class StockUrgenciaService:
    @staticmethod
    @transaction.atomic
    def registar_movimento(
        medicamento: MedicamentoUrgencia,
        *,
        tipo: str,
        quantidade: int,
        motivo: str = "",
        operador=None,
    ) -> MovimentoStockUrgencia:
        if quantidade <= 0:
            raise StockUrgenciaError("A quantidade deve ser superior a zero.")
        antes = medicamento.quantidade_stock
        if tipo == TipoMovimentoStockUrgencia.ENTRADA:
            depois = antes + quantidade
        elif tipo == TipoMovimentoStockUrgencia.SAIDA:
            if quantidade > antes:
                raise StockUrgenciaError("Stock insuficiente para esta saída.")
            depois = antes - quantidade
        elif tipo == TipoMovimentoStockUrgencia.AJUSTE:
            depois = quantidade
            quantidade = abs(depois - antes) or quantidade
        else:
            raise StockUrgenciaError("Tipo de movimento inválido.")

        medicamento.quantidade_stock = depois
        medicamento.save(update_fields=["quantidade_stock", "updated_at"])

        return MovimentoStockUrgencia.objects.create(
            medicamento=medicamento,
            tipo=tipo,
            quantidade=quantidade,
            quantidade_antes=antes,
            quantidade_depois=depois,
            motivo=motivo.strip(),
            operador=operador,
        )
