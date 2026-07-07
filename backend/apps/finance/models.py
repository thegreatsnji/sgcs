"""Modelos do módulo Financeiro."""

from decimal import Decimal

from django.conf import settings
from django.db import models

from apps.finance.constants import (
    CaixaEstado,
    CategoriaTipo,
    DEFAULT_DESPESA_CATEGORIA,
    DESPESA_CATEGORIAS,
    DespesaEstado,
    MovimentoOrigem,
    MovimentoTipo,
)
from core.mixins import TimestampMixin


class CategoriaFinanceira(TimestampMixin):
    nome = models.CharField("Nome", max_length=100)
    tipo = models.CharField("Tipo", max_length=10, choices=CategoriaTipo.choices)
    descricao = models.TextField("Descrição", blank=True)
    activa = models.BooleanField("Activa", default=True)

    class Meta:
        verbose_name = "Categoria financeira"
        verbose_name_plural = "Categorias financeiras"
        ordering = ["tipo", "nome"]
        unique_together = [("nome", "tipo")]

    def __str__(self) -> str:
        return f"{self.nome} ({self.get_tipo_display()})"


class Caixa(TimestampMixin):
    codigo = models.CharField("Código", max_length=30, unique=True)
    nome = models.CharField("Nome", max_length=120)
    estado = models.CharField(
        "Estado",
        max_length=10,
        choices=CaixaEstado.choices,
        default=CaixaEstado.FECHADO,
    )
    saldo_inicial = models.DecimalField(
        "Saldo inicial", max_digits=14, decimal_places=2, default=Decimal("0.00")
    )
    saldo_actual = models.DecimalField(
        "Saldo actual", max_digits=14, decimal_places=2, default=Decimal("0.00")
    )
    data_abertura = models.DateTimeField("Data de abertura", null=True, blank=True)
    data_fecho = models.DateTimeField("Data de fecho", null=True, blank=True)
    utilizador_abertura = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="caixas_abertas",
        verbose_name="Utilizador de abertura",
    )
    utilizador_fecho = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="caixas_fechadas",
        verbose_name="Utilizador de fecho",
    )
    observacoes = models.TextField("Observações", blank=True)

    class Meta:
        verbose_name = "Caixa"
        verbose_name_plural = "Caixas"
        ordering = ["codigo"]

    def __str__(self) -> str:
        return f"{self.codigo} — {self.nome}"


class MovimentoFinanceiro(TimestampMixin):
    caixa = models.ForeignKey(
        Caixa,
        on_delete=models.PROTECT,
        related_name="movimentos",
        verbose_name="Caixa",
    )
    tipo = models.CharField("Tipo", max_length=15, choices=MovimentoTipo.choices)
    origem = models.CharField("Origem", max_length=15, choices=MovimentoOrigem.choices)
    valor = models.DecimalField("Valor", max_digits=14, decimal_places=2)
    descricao = models.CharField("Descrição", max_length=255)
    referencia = models.CharField("Referência", max_length=100, blank=True)
    pagamento = models.ForeignKey(
        "billing.Pagamento",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="movimentos_financeiros",
        verbose_name="Pagamento",
    )
    despesa = models.ForeignKey(
        "finance.Despesa",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="movimentos",
        verbose_name="Despesa",
    )
    utilizador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="movimentos_financeiros",
        verbose_name="Utilizador",
    )
    data = models.DateTimeField("Data")

    class Meta:
        verbose_name = "Movimento financeiro"
        verbose_name_plural = "Movimentos financeiros"
        ordering = ["-data"]
        indexes = [
            models.Index(fields=["tipo", "data"], name="idx_fin_mov_tipo_data"),
            models.Index(fields=["caixa", "data"], name="idx_fin_mov_caixa_data"),
        ]

    def __str__(self) -> str:
        return f"{self.tipo} {self.valor} — {self.caixa.codigo}"


class Despesa(TimestampMixin):
    fornecedor = models.CharField("Fornecedor", max_length=150)
    categoria = models.CharField(
        "Categoria",
        max_length=30,
        choices=DESPESA_CATEGORIAS,
        default=DEFAULT_DESPESA_CATEGORIA,
    )
    categoria_financeira = models.ForeignKey(
        CategoriaFinanceira,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="despesas",
        verbose_name="Categoria financeira",
    )
    valor = models.DecimalField("Valor", max_digits=14, decimal_places=2)
    descricao = models.TextField("Descrição")
    estado = models.CharField(
        "Estado",
        max_length=15,
        choices=DespesaEstado.choices,
        default=DespesaEstado.PENDENTE,
    )
    data = models.DateField("Data")
    observacoes = models.TextField("Observações", blank=True)
    criado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="despesas_criadas",
        verbose_name="Criado por",
    )

    class Meta:
        verbose_name = "Despesa"
        verbose_name_plural = "Despesas"
        ordering = ["-data", "-created_at"]
        indexes = [
            models.Index(fields=["estado", "data"], name="idx_fin_desp_estado_data"),
        ]

    def __str__(self) -> str:
        return f"{self.fornecedor} — {self.valor}"
