"""Modelos do módulo de Faturação."""

from decimal import Decimal

from django.conf import settings
from django.db import models

from apps.billing.constants import (
    DEFAULT_SERVICE_CATEGORY,
    FaturaEstado,
    MetodoPagamento,
    OrcamentoEstado,
    PagamentoEstado,
    SERVICE_CATEGORIES,
)
from core.mixins import TimestampMixin


class Servico(TimestampMixin):
    codigo = models.CharField("Código", max_length=30, unique=True)
    nome = models.CharField("Nome", max_length=150)
    descricao = models.TextField("Descrição", blank=True)
    categoria = models.CharField(
        "Categoria",
        max_length=30,
        choices=SERVICE_CATEGORIES,
        default=DEFAULT_SERVICE_CATEGORY,
    )
    preco = models.DecimalField("Preço", max_digits=12, decimal_places=2, default=Decimal("0.00"))
    activo = models.BooleanField("Activo", default=True)

    class Meta:
        verbose_name = "Serviço"
        verbose_name_plural = "Serviços"
        ordering = ["nome"]
        indexes = [
            models.Index(fields=["activo", "categoria"], name="idx_bill_svc_act_cat"),
        ]

    def __str__(self) -> str:
        return f"{self.codigo} — {self.nome}"


class Orcamento(TimestampMixin):
    numero = models.CharField("Número", max_length=20, unique=True)
    paciente = models.ForeignKey(
        "patients.Patient",
        on_delete=models.PROTECT,
        related_name="orcamentos",
        verbose_name="Paciente",
    )
    criado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orcamentos_criados",
        verbose_name="Criado por",
    )
    estado = models.CharField(
        "Estado",
        max_length=20,
        choices=OrcamentoEstado.choices,
        default=OrcamentoEstado.RASCUNHO,
    )
    subtotal = models.DecimalField("Subtotal", max_digits=12, decimal_places=2, default=Decimal("0.00"))
    desconto = models.DecimalField("Desconto", max_digits=12, decimal_places=2, default=Decimal("0.00"))
    imposto = models.DecimalField("Imposto", max_digits=12, decimal_places=2, default=Decimal("0.00"))
    total = models.DecimalField("Total", max_digits=12, decimal_places=2, default=Decimal("0.00"))
    validade = models.DateField("Validade", null=True, blank=True)

    class Meta:
        verbose_name = "Orçamento"
        verbose_name_plural = "Orçamentos"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["estado", "created_at"], name="idx_bill_orc_estado"),
            models.Index(fields=["paciente", "created_at"], name="idx_bill_orc_paciente"),
        ]

    def __str__(self) -> str:
        return f"{self.numero} — {self.paciente.full_name}"

    @property
    def is_editavel(self) -> bool:
        from apps.billing.constants import ORCAMENTO_EDITABLE_STATUSES

        return self.estado in ORCAMENTO_EDITABLE_STATUSES


class ItemOrcamento(TimestampMixin):
    orcamento = models.ForeignKey(
        Orcamento,
        on_delete=models.CASCADE,
        related_name="itens",
        verbose_name="Orçamento",
    )
    servico = models.ForeignKey(
        Servico,
        on_delete=models.PROTECT,
        related_name="itens_orcamento",
        verbose_name="Serviço",
    )
    quantidade = models.PositiveIntegerField("Quantidade", default=1)
    preco_unitario = models.DecimalField("Preço unitário", max_digits=12, decimal_places=2)
    subtotal = models.DecimalField("Subtotal", max_digits=12, decimal_places=2)

    class Meta:
        verbose_name = "Item de orçamento"
        verbose_name_plural = "Itens de orçamento"
        ordering = ["id"]

    def __str__(self) -> str:
        return f"{self.servico.nome} x{self.quantidade}"


class Fatura(TimestampMixin):
    numero = models.CharField("Número", max_length=20, unique=True)
    paciente = models.ForeignKey(
        "patients.Patient",
        on_delete=models.PROTECT,
        related_name="faturas",
        verbose_name="Paciente",
    )
    consulta = models.OneToOneField(
        "appointments.Appointment",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="fatura",
        verbose_name="Consulta",
    )
    orcamento = models.ForeignKey(
        Orcamento,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="faturas",
        verbose_name="Orçamento",
    )
    estado = models.CharField(
        "Estado",
        max_length=20,
        choices=FaturaEstado.choices,
        default=FaturaEstado.PENDENTE,
    )
    subtotal = models.DecimalField("Subtotal", max_digits=12, decimal_places=2, default=Decimal("0.00"))
    desconto = models.DecimalField("Desconto", max_digits=12, decimal_places=2, default=Decimal("0.00"))
    imposto = models.DecimalField("Imposto", max_digits=12, decimal_places=2, default=Decimal("0.00"))
    total = models.DecimalField("Total", max_digits=12, decimal_places=2, default=Decimal("0.00"))
    emitida_em = models.DateTimeField("Emitida em", null=True, blank=True)
    emitida_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="faturas_emitidas",
        verbose_name="Emitida por",
    )

    class Meta:
        verbose_name = "Fatura"
        verbose_name_plural = "Faturas"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["estado", "emitida_em"], name="idx_bill_fat_estado"),
            models.Index(fields=["paciente", "emitida_em"], name="idx_bill_fat_paciente"),
        ]

    def __str__(self) -> str:
        return f"{self.numero} — {self.paciente.full_name}"

    @property
    def is_editavel(self) -> bool:
        from apps.billing.constants import FATURA_EDITABLE_STATUSES

        return self.estado in FATURA_EDITABLE_STATUSES

    @property
    def total_pago(self) -> Decimal:
        return (
            self.pagamentos.filter(estado=PagamentoEstado.CONFIRMADO).aggregate(
                total=models.Sum("valor")
            )["total"]
            or Decimal("0.00")
        )


class ItemFatura(TimestampMixin):
    fatura = models.ForeignKey(
        Fatura,
        on_delete=models.CASCADE,
        related_name="itens",
        verbose_name="Fatura",
    )
    servico = models.ForeignKey(
        Servico,
        on_delete=models.PROTECT,
        related_name="itens_fatura",
        verbose_name="Serviço",
    )
    quantidade = models.PositiveIntegerField("Quantidade", default=1)
    preco = models.DecimalField("Preço", max_digits=12, decimal_places=2)
    subtotal = models.DecimalField("Subtotal", max_digits=12, decimal_places=2)

    class Meta:
        verbose_name = "Item de fatura"
        verbose_name_plural = "Itens de fatura"
        ordering = ["id"]

    def __str__(self) -> str:
        return f"{self.servico.nome} x{self.quantidade}"


class Pagamento(TimestampMixin):
    fatura = models.ForeignKey(
        Fatura,
        on_delete=models.PROTECT,
        related_name="pagamentos",
        verbose_name="Fatura",
    )
    metodo_pagamento = models.CharField(
        "Método de pagamento",
        max_length=20,
        choices=MetodoPagamento.choices,
        default=MetodoPagamento.DINHEIRO,
    )
    valor = models.DecimalField("Valor", max_digits=12, decimal_places=2)
    referencia = models.CharField("Referência", max_length=100, blank=True)
    estado = models.CharField(
        "Estado",
        max_length=20,
        choices=PagamentoEstado.choices,
        default=PagamentoEstado.PENDENTE,
    )
    recebido_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="pagamentos_recebidos",
        verbose_name="Recebido por",
    )
    data_pagamento = models.DateTimeField("Data de pagamento", null=True, blank=True)

    class Meta:
        verbose_name = "Pagamento"
        verbose_name_plural = "Pagamentos"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["estado", "data_pagamento"], name="idx_bill_pay_estado"),
        ]

    def __str__(self) -> str:
        return f"Pagamento {self.pk} — {self.fatura.numero}"


class Recibo(TimestampMixin):
    numero = models.CharField("Número", max_length=20, unique=True)
    pagamento = models.OneToOneField(
        Pagamento,
        on_delete=models.PROTECT,
        related_name="recibo",
        verbose_name="Pagamento",
    )
    emitido_em = models.DateTimeField("Emitido em", auto_now_add=True)

    class Meta:
        verbose_name = "Recibo"
        verbose_name_plural = "Recibos"
        ordering = ["-emitido_em"]

    def __str__(self) -> str:
        return f"{self.numero}"
