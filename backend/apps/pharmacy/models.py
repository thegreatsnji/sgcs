"""Stock de urgência — medicamentos e materiais clínicos (não é farmácia comercial)."""

from django.conf import settings
from django.db import models

from apps.pharmacy.constants import CategoriaItemUrgencia, OrigemMovimentoStock, TipoMovimentoStockUrgencia
from apps.pharmacy.status import estado_item
from core.mixins import TimestampMixin


class MedicamentoUrgencia(TimestampMixin):
    codigo = models.CharField("Código", max_length=40, unique=True)
    nome = models.CharField("Nome", max_length=200)
    forma_apresentacao = models.CharField("Apresentação", max_length=100, blank=True)
    categoria = models.CharField(
        "Categoria",
        max_length=30,
        choices=CategoriaItemUrgencia.choices,
        default=CategoriaItemUrgencia.MEDICAMENTO,
    )
    unidade = models.CharField("Unidade", max_length=30, default="unidade")
    quantidade_stock = models.PositiveIntegerField("Quantidade actual", default=0)
    stock_minimo = models.PositiveIntegerField("Stock mínimo", default=5)
    validade = models.DateField("Validade", null=True, blank=True)
    preco_referencia_fcfa = models.DecimalField(
        "Preço de referência (FCFA)",
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
    )
    quantidade_texto_original = models.CharField(
        "Quantidade (texto original)",
        max_length=40,
        blank=True,
        help_text="Texto das fotografias (ex.: CX/50). Não é saldo físico.",
    )
    servico = models.ForeignKey(
        "billing.Servico",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="medicamentos_urgencia",
        verbose_name="Serviço de faturação (opcional)",
    )
    activo = models.BooleanField("Activo", default=True)
    observacoes = models.TextField("Observações", blank=True)

    class Meta:
        verbose_name = "Item de stock de urgência"
        verbose_name_plural = "Itens de stock de urgência"
        ordering = ["nome"]

    def __str__(self) -> str:
        return f"{self.codigo} — {self.nome}"

    @property
    def abaixo_minimo(self) -> bool:
        return self.quantidade_stock <= self.stock_minimo

    @property
    def estado(self) -> str:
        return estado_item(
            quantidade=self.quantidade_stock,
            stock_minimo=self.stock_minimo,
            validade=self.validade,
        )

    @property
    def stock_inicial_por_confirmar(self) -> bool:
        from apps.pharmacy.services.stock_service import StockUrgenciaService

        return StockUrgenciaService.stock_inicial_por_confirmar(self)


class MovimentoStockUrgencia(TimestampMixin):
    medicamento = models.ForeignKey(
        MedicamentoUrgencia,
        on_delete=models.PROTECT,
        related_name="movimentos",
        verbose_name="Item",
    )
    tipo = models.CharField("Tipo", max_length=20, choices=TipoMovimentoStockUrgencia.choices)
    quantidade = models.PositiveIntegerField("Quantidade")
    quantidade_antes = models.PositiveIntegerField("Stock antes")
    quantidade_depois = models.PositiveIntegerField("Stock depois")
    motivo = models.CharField("Observação", max_length=255, blank=True)
    origem = models.CharField(
        "Origem",
        max_length=32,
        choices=OrigemMovimentoStock.choices,
        default=OrigemMovimentoStock.MANUAL,
    )
    operador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="movimentos_farmacia_urgencia",
        verbose_name="Utilizador",
    )
    paciente = models.ForeignKey(
        "patients.Patient",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="movimentos_stock_urgencia",
        verbose_name="Utente",
    )
    consulta = models.ForeignKey(
        "appointments.Appointment",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="movimentos_stock_urgencia",
        verbose_name="Consulta",
    )

    class Meta:
        verbose_name = "Movimento de stock de urgência"
        verbose_name_plural = "Movimentos de stock de urgência"
        ordering = ["-created_at"]
        default_permissions = ("add", "view")

    def __str__(self) -> str:
        return f"{self.tipo} {self.quantidade} {self.medicamento_id}"

    def save(self, *args, **kwargs):
        if self.pk:
            raise ValueError("Os movimentos de stock não podem ser alterados.")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValueError("Os movimentos de stock não podem ser apagados.")
