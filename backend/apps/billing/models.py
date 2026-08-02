"""Modelos do módulo de Faturação."""

from decimal import Decimal

from django.conf import settings
from django.db import models

from apps.billing.constants import (
    DEFAULT_BILLING_UNIT,
    DEFAULT_SERVICE_CATEGORY,
    DEFAULT_SERVICE_CURRENCY,
    EstadoAutorizacaoReducao,
    FaturaEstado,
    MetodoPagamento,
    MotivoReducao,
    OrcamentoEstado,
    OrigemPrecoItem,
    PagamentoEstado,
    SERVICE_CATEGORIES,
)
from core.mixins import TimestampMixin


class Servico(TimestampMixin):
    codigo = models.CharField("Código", max_length=64, unique=True)
    nome = models.CharField("Nome", max_length=150)
    descricao = models.TextField("Descrição", blank=True)
    categoria = models.CharField(
        "Categoria",
        max_length=30,
        choices=SERVICE_CATEGORIES,
        default=DEFAULT_SERVICE_CATEGORY,
    )
    departamento = models.ForeignKey(
        "clinic_settings.Departamento",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="servicos",
        verbose_name="Departamento",
    )
    especialidade = models.ForeignKey(
        "clinic_settings.EspecialidadeMedica",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="servicos",
        verbose_name="Especialidade",
    )
    preco = models.DecimalField("Preço", max_digits=12, decimal_places=2, default=Decimal("0.00"))
    preco_confirmado = models.BooleanField("Preço confirmado pela clínica", default=False)
    preco_confirmado_em = models.DateTimeField("Preço confirmado em", null=True, blank=True)
    preco_confirmado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="servicos_preco_confirmado",
        verbose_name="Preço confirmado por",
    )
    permite_faturacao_sem_preco_confirmado = models.BooleanField(
        "Autorização temporária de faturação (admin)",
        default=False,
    )
    moeda = models.CharField("Moeda", max_length=10, default=DEFAULT_SERVICE_CURRENCY)
    activo = models.BooleanField("Activo", default=True)
    exige_pedido_medico = models.BooleanField("Exige pedido médico", default=False)
    exige_pagamento_antecipado = models.BooleanField("Exige pagamento antecipado", default=False)
    permite_pagamento_parcial = models.BooleanField("Permite pagamento parcial", default=True)
    exige_agendamento = models.BooleanField("Exige agendamento", default=False)
    gera_resultado = models.BooleanField("Gera resultado", default=False)
    duracao_minutos = models.PositiveIntegerField("Duração (min)", null=True, blank=True)
    unidade_cobranca = models.CharField("Unidade de cobrança", max_length=30, default=DEFAULT_BILLING_UNIT)
    ordem = models.PositiveIntegerField("Ordem", default=0)
    observacoes = models.TextField("Observações", blank=True)
    versao_catalogo = models.CharField(
        "Versão do catálogo",
        max_length=40,
        blank=True,
        db_index=True,
        help_text="Ex.: SAUVIDA_V1 — vazio para legado",
    )
    arquivado = models.BooleanField(
        "Arquivado (fora da receção)",
        default=False,
        db_index=True,
    )
    criado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="servicos_criados",
        verbose_name="Criado por",
    )
    actualizado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="servicos_actualizados",
        verbose_name="Actualizado por",
    )

    class Meta:
        verbose_name = "Serviço"
        verbose_name_plural = "Serviços"
        ordering = ["ordem", "nome"]
        indexes = [
            models.Index(fields=["activo", "categoria"], name="idx_bill_svc_act_cat"),
            models.Index(fields=["departamento", "activo"], name="idx_bill_svc_dept_act"),
            models.Index(fields=["preco_confirmado", "activo"], name="idx_bill_svc_preco_conf"),
        ]

    @property
    def estado_validacao_preco(self) -> str:
        if self.preco_confirmado:
            return "CONFIRMADO"
        if self.permite_faturacao_sem_preco_confirmado:
            return "NECESSITA_REVISAO"
        return "PENDENTE"

    def pode_faturar(self, user=None) -> bool:
        from apps.billing.services.catalog_service import servico_pode_faturar

        return servico_pode_faturar(self, user)

    def __str__(self) -> str:
        return f"{self.codigo} — {self.nome}"


class ServicoPrecoHistorico(TimestampMixin):
    servico = models.ForeignKey(
        Servico,
        on_delete=models.CASCADE,
        related_name="historico_precos",
        verbose_name="Serviço",
    )
    preco_anterior = models.DecimalField("Preço anterior", max_digits=12, decimal_places=2)
    preco_novo = models.DecimalField("Preço novo", max_digits=12, decimal_places=2)
    motivo = models.CharField("Motivo", max_length=255, blank=True)
    origem = models.CharField("Origem", max_length=30, default="manual")
    alterado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="alteracoes_preco_servico",
        verbose_name="Alterado por",
    )
    ip_address = models.GenericIPAddressField("IP", null=True, blank=True)

    class Meta:
        verbose_name = "Histórico de preço"
        verbose_name_plural = "Histórico de preços"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.servico.codigo}: {self.preco_anterior} → {self.preco_novo}"


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
    preco = models.DecimalField(
        "Preço cobrado (un.)",
        max_digits=12,
        decimal_places=2,
        help_text="Snapshot do valor efectivamente cobrado por unidade.",
    )
    preco_oficial = models.DecimalField(
        "Preço oficial (un.)",
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    subtotal = models.DecimalField("Subtotal cobrado", max_digits=12, decimal_places=2)
    subtotal_oficial = models.DecimalField(
        "Subtotal oficial",
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    valor_reducao = models.DecimalField(
        "Valor da redução (total linha)",
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    percentual_reducao = models.DecimalField(
        "Percentual de redução",
        max_digits=7,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    motivo_reducao = models.CharField(
        "Motivo da redução",
        max_length=40,
        choices=MotivoReducao.choices,
        blank=True,
    )
    observacao_reducao = models.TextField("Observação da redução", blank=True)
    origem_preco = models.CharField(
        "Origem do preço cobrado",
        max_length=30,
        choices=OrigemPrecoItem.choices,
        default=OrigemPrecoItem.CATALOGO,
    )
    estado_autorizacao_reducao = models.CharField(
        "Estado da autorização",
        max_length=30,
        choices=EstadoAutorizacaoReducao.choices,
        default=EstadoAutorizacaoReducao.NAO_APLICAVEL,
    )
    reduzido_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="itens_fatura_reduzidos",
        verbose_name="Redução aplicada por",
    )
    autorizado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="itens_fatura_reducao_autorizados",
        verbose_name="Autorizado por",
    )
    data_reducao = models.DateTimeField("Data da redução", null=True, blank=True)
    autorizacao_reducao = models.ForeignKey(
        "billing.ReducaoValorAutorizacao",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="itens_fatura",
        verbose_name="Autorização de redução",
    )

    class Meta:
        verbose_name = "Item de fatura"
        verbose_name_plural = "Itens de fatura"
        ordering = ["id"]

    def __str__(self) -> str:
        return f"{self.servico.nome} x{self.quantidade}"


class ReducaoValorAutorizacao(TimestampMixin):
    servico = models.ForeignKey(
        Servico,
        on_delete=models.PROTECT,
        related_name="autorizacoes_reducao",
        verbose_name="Serviço",
    )
    paciente = models.ForeignKey(
        "patients.Patient",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="autorizacoes_reducao",
        verbose_name="Paciente",
    )
    fatura = models.ForeignKey(
        Fatura,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="autorizacoes_reducao",
        verbose_name="Fatura",
    )
    solicitado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="reducoes_solicitadas",
        verbose_name="Solicitado por",
    )
    solicitado_em = models.DateTimeField("Solicitado em", auto_now_add=True)
    motivo_reducao = models.CharField(
        "Motivo",
        max_length=40,
        choices=MotivoReducao.choices,
    )
    observacao_solicitacao = models.TextField("Observação", blank=True)
    preco_oficial = models.DecimalField("Preço oficial", max_digits=12, decimal_places=2)
    preco_proposto = models.DecimalField("Preço proposto", max_digits=12, decimal_places=2)
    quantidade = models.PositiveIntegerField("Quantidade", default=1)
    diferenca_unitaria = models.DecimalField("Diferença (un.)", max_digits=12, decimal_places=2)
    percentual_reducao = models.DecimalField("Percentual", max_digits=7, decimal_places=2)
    estado = models.CharField(
        "Estado",
        max_length=30,
        choices=EstadoAutorizacaoReducao.choices,
        default=EstadoAutorizacaoReducao.PENDENTE,
    )
    decidido_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reducoes_decididas",
        verbose_name="Decidido por",
    )
    decidido_em = models.DateTimeField("Decidido em", null=True, blank=True)
    observacao_decisao = models.TextField("Observação da decisão", blank=True)

    class Meta:
        verbose_name = "Autorização de redução de valor"
        verbose_name_plural = "Autorizações de redução de valor"
        ordering = ["-solicitado_em"]
        indexes = [
            models.Index(fields=["estado", "solicitado_em"], name="idx_bill_red_estado"),
        ]

    def __str__(self) -> str:
        return f"Redução {self.servico.codigo} — {self.estado}"


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
    segunda_via = models.BooleanField("Segunda via", default=False)
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
