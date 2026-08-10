"""Stock de medicamentos para urgência (âmbito limitado — não farmácia comercial)."""

from django.conf import settings
from django.db import models

from apps.pharmacy.constants import TipoMovimentoStockUrgencia
from core.mixins import TimestampMixin


class MedicamentoUrgencia(TimestampMixin):
    codigo = models.CharField("Código", max_length=40, unique=True)
    nome = models.CharField("Nome", max_length=200)
    forma_apresentacao = models.CharField("Forma", max_length=100, blank=True)
    unidade = models.CharField("Unidade", max_length=30, default="unidade")
    quantidade_stock = models.PositiveIntegerField("Quantidade em stock", default=0)
    stock_minimo = models.PositiveIntegerField("Stock mínimo", default=5)
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
        verbose_name = "Medicamento de urgência"
        verbose_name_plural = "Medicamentos de urgência"
        ordering = ["nome"]

    def __str__(self) -> str:
        return f"{self.codigo} — {self.nome}"

    @property
    def abaixo_minimo(self) -> bool:
        return self.quantidade_stock <= self.stock_minimo


class MovimentoStockUrgencia(TimestampMixin):
    medicamento = models.ForeignKey(
        MedicamentoUrgencia,
        on_delete=models.PROTECT,
        related_name="movimentos",
        verbose_name="Medicamento",
    )
    tipo = models.CharField(
        "Tipo",
        max_length=20,
        choices=TipoMovimentoStockUrgencia.choices,
    )
    quantidade = models.PositiveIntegerField("Quantidade")
    quantidade_antes = models.PositiveIntegerField("Stock antes")
    quantidade_depois = models.PositiveIntegerField("Stock depois")
    motivo = models.CharField("Motivo", max_length=255, blank=True)
    operador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="movimentos_farmacia_urgencia",
        verbose_name="Operador",
    )

    class Meta:
        verbose_name = "Movimento de stock (urgência)"
        verbose_name_plural = "Movimentos de stock (urgência)"
        ordering = ["-created_at"]
