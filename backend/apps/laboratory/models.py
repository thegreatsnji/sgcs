"""Modelos do módulo Laboratório."""

from django.conf import settings
from django.db import models

from apps.laboratory.constants import (
    DEFAULT_EXAM_CATEGORY,
    EXAM_CATEGORIES,
    InterpretacaoParametro,
    PedidoLaboratorialEstado,
    ResultadoLaboratorialEstado,
    TipoAnexoResultado,
)
from apps.reception.constants import QueuePriority
from core.mixins import TimestampMixin


class PedidoLaboratorial(TimestampMixin):
    numero_pedido = models.CharField("Número do pedido", max_length=20, unique=True)
    consulta = models.ForeignKey(
        "appointments.Appointment",
        on_delete=models.PROTECT,
        related_name="pedidos_laboratoriais",
        verbose_name="Consulta",
    )
    paciente = models.ForeignKey(
        "patients.Patient",
        on_delete=models.PROTECT,
        related_name="pedidos_laboratoriais",
        verbose_name="Paciente",
    )
    medico = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="pedidos_laboratoriais_solicitados",
        verbose_name="Médico",
    )
    pedido_consulta = models.OneToOneField(
        "appointments.PedidoLaboratorio",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="pedido_laboratorial",
        verbose_name="Pedido na consulta",
    )
    estado = models.CharField(
        "Estado",
        max_length=25,
        choices=PedidoLaboratorialEstado.choices,
        default=PedidoLaboratorialEstado.PENDENTE,
    )
    prioridade = models.CharField(
        "Prioridade",
        max_length=20,
        choices=QueuePriority.choices,
        default=QueuePriority.NORMAL,
    )
    data_pedido = models.DateTimeField("Data do pedido", auto_now_add=True)
    data_rececao = models.DateTimeField("Data de receção", null=True, blank=True)
    data_colheita = models.DateTimeField("Data de colheita", null=True, blank=True)
    data_conclusao = models.DateTimeField("Data de conclusão", null=True, blank=True)
    observacoes = models.TextField("Observações", blank=True)
    registado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="pedidos_lab_registados",
        verbose_name="Registado por",
    )

    class Meta:
        verbose_name = "Pedido laboratorial"
        verbose_name_plural = "Pedidos laboratoriais"
        ordering = ["-data_pedido"]
        indexes = [
            models.Index(fields=["estado", "data_pedido"], name="idx_lab_ped_estado_data"),
            models.Index(fields=["paciente", "data_pedido"], name="idx_lab_ped_paciente"),
            models.Index(fields=["numero_pedido"], name="idx_lab_ped_numero"),
        ]

    def __str__(self) -> str:
        return f"{self.numero_pedido} — {self.paciente.full_name}"

    @property
    def is_finalizado(self) -> bool:
        return self.estado in {
            PedidoLaboratorialEstado.CONCLUIDO,
            PedidoLaboratorialEstado.CANCELADO,
        }


class ExameLaboratorial(TimestampMixin):
    pedido = models.ForeignKey(
        PedidoLaboratorial,
        on_delete=models.CASCADE,
        related_name="exames",
        verbose_name="Pedido",
    )
    nome_exame = models.CharField("Nome do exame", max_length=150)
    categoria = models.CharField(
        "Categoria",
        max_length=30,
        choices=EXAM_CATEGORIES,
        default=DEFAULT_EXAM_CATEGORY,
    )
    estado = models.CharField(
        "Estado",
        max_length=25,
        choices=PedidoLaboratorialEstado.choices,
        default=PedidoLaboratorialEstado.PENDENTE,
    )
    observacoes = models.TextField("Observações", blank=True)

    class Meta:
        verbose_name = "Exame laboratorial"
        verbose_name_plural = "Exames laboratoriais"
        ordering = ["id"]

    def __str__(self) -> str:
        return f"{self.nome_exame} ({self.pedido.numero_pedido})"


class ResultadoLaboratorial(TimestampMixin):
    pedido_laboratorial = models.OneToOneField(
        PedidoLaboratorial,
        on_delete=models.CASCADE,
        related_name="resultado",
        verbose_name="Pedido laboratorial",
    )
    estado = models.CharField(
        "Estado",
        max_length=25,
        choices=ResultadoLaboratorialEstado.choices,
        default=ResultadoLaboratorialEstado.EM_PROCESSAMENTO,
    )
    responsavel = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="resultados_laboratoriais",
        verbose_name="Responsável",
    )
    validado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="resultados_validados",
        verbose_name="Validado por",
    )
    data_resultado = models.DateTimeField("Data do resultado", null=True, blank=True)
    data_validacao = models.DateTimeField("Data de validação", null=True, blank=True)
    data_publicacao = models.DateTimeField("Data de publicação", null=True, blank=True)
    observacoes = models.TextField("Observações", blank=True)
    conclusao = models.TextField("Conclusão", blank=True)

    class Meta:
        verbose_name = "Resultado laboratorial"
        verbose_name_plural = "Resultados laboratoriais"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["estado", "data_resultado"], name="idx_lab_res_estado_data"),
        ]

    def __str__(self) -> str:
        return f"Resultado — {self.pedido_laboratorial.numero_pedido}"

    @property
    def is_editavel(self) -> bool:
        from apps.laboratory.constants import RESULTADO_EDITABLE_STATUSES

        return self.estado in RESULTADO_EDITABLE_STATUSES


class ParametroResultado(TimestampMixin):
    resultado = models.ForeignKey(
        ResultadoLaboratorial,
        on_delete=models.CASCADE,
        related_name="parametros",
        verbose_name="Resultado",
    )
    nome = models.CharField("Nome", max_length=120)
    valor = models.CharField("Valor", max_length=100)
    unidade = models.CharField("Unidade", max_length=30, blank=True)
    valor_minimo = models.CharField("Valor mínimo", max_length=30, blank=True)
    valor_maximo = models.CharField("Valor máximo", max_length=30, blank=True)
    interpretacao = models.CharField(
        "Interpretação",
        max_length=20,
        choices=InterpretacaoParametro.choices,
        default=InterpretacaoParametro.NORMAL,
    )
    ordem = models.PositiveSmallIntegerField("Ordem", default=0)

    class Meta:
        verbose_name = "Parâmetro de resultado"
        verbose_name_plural = "Parâmetros de resultado"
        ordering = ["ordem", "id"]

    def __str__(self) -> str:
        return f"{self.nome}: {self.valor} {self.unidade}".strip()


class AnexoResultado(TimestampMixin):
    resultado = models.ForeignKey(
        ResultadoLaboratorial,
        on_delete=models.CASCADE,
        related_name="anexos",
        verbose_name="Resultado",
    )
    ficheiro = models.ForeignKey(
        "files.StoredFile",
        on_delete=models.PROTECT,
        related_name="anexos_resultado_laboratorial",
        verbose_name="Ficheiro",
    )
    tipo = models.CharField(
        "Tipo",
        max_length=10,
        choices=TipoAnexoResultado.choices,
    )
    descricao = models.CharField("Descrição", max_length=255, blank=True)

    class Meta:
        verbose_name = "Anexo de resultado"
        verbose_name_plural = "Anexos de resultado"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.tipo} — {self.resultado}"
