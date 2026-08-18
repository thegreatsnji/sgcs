from django.db import transaction
from django.db.models import Max

from apps.audit_logs.models import AuditAction
from apps.audit_logs.services import AuditService
from apps.pharmacy.constants import OrigemMovimentoStock, TipoMovimentoStockUrgencia
from apps.pharmacy.models import MedicamentoUrgencia, MovimentoStockUrgencia


class StockUrgenciaError(Exception):
    pass


AUDIT_BY_TYPE = {
    TipoMovimentoStockUrgencia.ENTRADA: AuditAction.STOCK_ENTRADA,
    TipoMovimentoStockUrgencia.SAIDA: AuditAction.STOCK_SAIDA,
    TipoMovimentoStockUrgencia.AJUSTE: AuditAction.STOCK_AJUSTE,
    TipoMovimentoStockUrgencia.PERDA_EXPIRACAO: AuditAction.STOCK_PERDA_EXPIRACAO,
}


class StockUrgenciaService:
    @staticmethod
    def proximo_codigo() -> str:
        last = MedicamentoUrgencia.objects.aggregate(m=Max("id"))["m"] or 0
        return f"STK-{last + 1:05d}"

    @staticmethod
    @transaction.atomic
    def criar_item(
        *,
        nome: str,
        categoria: str,
        unidade: str,
        quantidade_inicial: int = 0,
        forma_apresentacao: str = "",
        stock_minimo: int = 5,
        validade=None,
        preco_referencia_fcfa=None,
        observacoes: str = "",
        quantidade_texto_original: str = "",
        codigo: str = "",
        operador=None,
        request=None,
        origem: str = OrigemMovimentoStock.STOCK_INICIAL,
    ) -> MedicamentoUrgencia:
        if quantidade_inicial < 0:
            raise StockUrgenciaError("A quantidade inicial não pode ser negativa.")
        item = MedicamentoUrgencia.objects.create(
            codigo=(codigo or StockUrgenciaService.proximo_codigo()).strip(),
            nome=nome.strip(),
            forma_apresentacao=(forma_apresentacao or "").strip(),
            categoria=categoria,
            unidade=(unidade or "unidade").strip(),
            quantidade_stock=0,
            stock_minimo=max(0, stock_minimo),
            validade=validade,
            preco_referencia_fcfa=preco_referencia_fcfa,
            quantidade_texto_original=(quantidade_texto_original or "").strip(),
            observacoes=(observacoes or "").strip(),
        )
        if quantidade_inicial > 0:
            StockUrgenciaService.registar_movimento(
                item,
                tipo=TipoMovimentoStockUrgencia.ENTRADA,
                quantidade=quantidade_inicial,
                motivo="Stock inicial",
                operador=operador,
                origem=origem,
                request=request,
            )
        AuditService.log(
            action=AuditAction.STOCK_ITEM_CRIADO,
            user=operador,
            request=request,
            description=f"Item de stock criado: {item.nome} ({item.codigo}).",
            resource_type="stock_urgencia",
            resource_id=item.pk,
            metadata={"codigo": item.codigo, "quantidade_inicial": quantidade_inicial},
        )
        item.refresh_from_db()
        return item

    @staticmethod
    @transaction.atomic
    def registar_movimento(
        medicamento: MedicamentoUrgencia,
        *,
        tipo: str,
        quantidade: int,
        motivo: str = "",
        operador=None,
        origem: str = OrigemMovimentoStock.MANUAL,
        paciente=None,
        consulta=None,
        request=None,
    ) -> MovimentoStockUrgencia:
        if quantidade <= 0:
            raise StockUrgenciaError("A quantidade deve ser superior a zero.")
        locked = MedicamentoUrgencia.objects.select_for_update().get(pk=medicamento.pk)
        antes = locked.quantidade_stock
        if tipo == TipoMovimentoStockUrgencia.ENTRADA:
            depois = antes + quantidade
            delta = quantidade
        elif tipo in {TipoMovimentoStockUrgencia.SAIDA, TipoMovimentoStockUrgencia.PERDA_EXPIRACAO}:
            if quantidade > antes:
                raise StockUrgenciaError("Stock insuficiente. Não é permitido stock negativo.")
            depois = antes - quantidade
            delta = quantidade
        elif tipo == TipoMovimentoStockUrgencia.AJUSTE:
            depois = quantidade
            if depois < 0:
                raise StockUrgenciaError("O ajuste não pode resultar em stock negativo.")
            delta = abs(depois - antes) or 1
        else:
            raise StockUrgenciaError("Tipo de movimento inválido.")

        locked.quantidade_stock = depois
        locked.save(update_fields=["quantidade_stock", "updated_at"])

        mov = MovimentoStockUrgencia.objects.create(
            medicamento=locked,
            tipo=tipo,
            quantidade=delta,
            quantidade_antes=antes,
            quantidade_depois=depois,
            motivo=(motivo or "").strip(),
            origem=origem,
            operador=operador,
            paciente=paciente,
            consulta=consulta,
        )
        AuditService.log(
            action=AUDIT_BY_TYPE[tipo],
            user=operador,
            request=request,
            description=f"{tipo} de {delta} em {locked.nome} ({antes} → {depois}).",
            resource_type="stock_urgencia",
            resource_id=locked.pk,
            metadata={
                "movimento_id": mov.pk,
                "tipo": tipo,
                "quantidade": delta,
                "antes": antes,
                "depois": depois,
                "paciente_id": getattr(paciente, "pk", None),
            },
        )
        medicamento.quantidade_stock = depois
        return mov
