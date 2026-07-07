"""Modelos do módulo Médicos."""

from django.conf import settings
from django.db import models

from apps.doctors.constants import (
    EvolucaoTipo,
    MedicamentoEstado,
    PrescricaoEstado,
    TratamentoEstado,
)
from core.mixins import TimestampMixin


class Prescricao(TimestampMixin):
    consulta = models.ForeignKey(
        "appointments.Appointment",
        on_delete=models.PROTECT,
        related_name="prescricoes_medicas",
        verbose_name="Consulta",
    )
    paciente = models.ForeignKey(
        "patients.Patient",
        on_delete=models.PROTECT,
        related_name="prescricoes",
        verbose_name="Paciente",
    )
    medico = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="prescricoes_emitidas",
        verbose_name="Médico",
    )
    estado = models.CharField(
        "Estado",
        max_length=20,
        choices=PrescricaoEstado.CHOICES,
        default=PrescricaoEstado.RASCUNHO,
    )
    observacoes = models.TextField("Observações", blank=True)

    class Meta:
        verbose_name = "Prescrição"
        verbose_name_plural = "Prescrições"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Prescrição #{self.pk} — {self.paciente}"


class MedicamentoPrescrito(TimestampMixin):
    prescricao = models.ForeignKey(
        Prescricao,
        on_delete=models.CASCADE,
        related_name="medicamentos",
        verbose_name="Prescrição",
    )
    nome = models.CharField("Nome", max_length=200)
    dosagem = models.CharField("Dosagem", max_length=100)
    forma_farmaceutica = models.CharField("Forma farmacêutica", max_length=100, blank=True)
    via = models.CharField("Via", max_length=50, blank=True)
    frequencia = models.CharField("Frequência", max_length=100)
    duracao = models.CharField("Duração", max_length=100)
    posologia = models.TextField("Posologia", blank=True)
    observacoes = models.TextField("Observações", blank=True)
    estado = models.CharField(
        "Estado",
        max_length=20,
        choices=MedicamentoEstado.CHOICES,
        default=MedicamentoEstado.ACTIVO,
    )

    class Meta:
        verbose_name = "Medicamento prescrito"
        verbose_name_plural = "Medicamentos prescritos"
        ordering = ["id"]

    def __str__(self) -> str:
        return f"{self.nome} — {self.prescricao_id}"


class PlanoTerapeutico(TimestampMixin):
    consulta = models.ForeignKey(
        "appointments.Appointment",
        on_delete=models.PROTECT,
        related_name="planos_terapeuticos",
        verbose_name="Consulta",
    )
    prescricao = models.ForeignKey(
        Prescricao,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="planos",
        verbose_name="Prescrição",
    )
    descricao = models.TextField("Descrição")
    objectivos = models.TextField("Objectivos", blank=True)
    duracao_prevista = models.CharField("Duração prevista", max_length=100, blank=True)

    class Meta:
        verbose_name = "Plano terapêutico"
        verbose_name_plural = "Planos terapêuticos"
        ordering = ["-created_at"]


class Tratamento(TimestampMixin):
    consulta = models.ForeignKey(
        "appointments.Appointment",
        on_delete=models.PROTECT,
        related_name="tratamentos_medicos",
        verbose_name="Consulta",
    )
    paciente = models.ForeignKey(
        "patients.Patient",
        on_delete=models.PROTECT,
        related_name="tratamentos",
        verbose_name="Paciente",
    )
    tipo = models.CharField("Tipo", max_length=100)
    descricao = models.TextField("Descrição")
    estado = models.CharField(
        "Estado",
        max_length=20,
        choices=TratamentoEstado.CHOICES,
        default=TratamentoEstado.EM_CURSO,
    )
    data_inicio = models.DateField("Data de início")
    data_fim = models.DateField("Data de fim", null=True, blank=True)
    responsavel = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tratamentos_responsavel",
        verbose_name="Responsável",
    )

    class Meta:
        verbose_name = "Tratamento"
        verbose_name_plural = "Tratamentos"
        ordering = ["-data_inicio"]


class EvolucaoClinica(TimestampMixin):
    consulta = models.ForeignKey(
        "appointments.Appointment",
        on_delete=models.PROTECT,
        related_name="evolucoes_clinicas",
        verbose_name="Consulta",
    )
    paciente = models.ForeignKey(
        "patients.Patient",
        on_delete=models.PROTECT,
        related_name="evolucoes_clinicas",
        verbose_name="Paciente",
    )
    tipo = models.CharField("Tipo", max_length=20, choices=EvolucaoTipo.CHOICES)
    observacoes = models.TextField("Observações")
    resposta_tratamento = models.TextField("Resposta ao tratamento", blank=True)
    registado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="evolucoes_registadas",
        verbose_name="Registado por",
    )

    class Meta:
        verbose_name = "Evolução clínica"
        verbose_name_plural = "Evoluções clínicas"
        ordering = ["-created_at"]


class AltaMedica(TimestampMixin):
    consulta = models.OneToOneField(
        "appointments.Appointment",
        on_delete=models.PROTECT,
        related_name="alta_medica",
        verbose_name="Consulta",
    )
    paciente = models.ForeignKey(
        "patients.Patient",
        on_delete=models.PROTECT,
        related_name="altas_medicas",
        verbose_name="Paciente",
    )
    medico = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="altas_emitidas",
        verbose_name="Médico",
    )
    motivo = models.TextField("Motivo")
    condicao = models.CharField("Condição", max_length=200)
    recomendacoes = models.TextField("Recomendações", blank=True)
    medicacao = models.TextField("Medicação", blank=True)
    seguimento = models.TextField("Seguimento", blank=True)
    restricoes = models.TextField("Restrições", blank=True)

    class Meta:
        verbose_name = "Alta médica"
        verbose_name_plural = "Altas médicas"
        ordering = ["-created_at"]


class SeguimentoClinico(TimestampMixin):
    consulta_origem = models.ForeignKey(
        "appointments.Appointment",
        on_delete=models.PROTECT,
        related_name="seguimentos_clinicos",
        verbose_name="Consulta de origem",
    )
    paciente = models.ForeignKey(
        "patients.Patient",
        on_delete=models.PROTECT,
        related_name="seguimentos_clinicos",
        verbose_name="Paciente",
    )
    medico = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="seguimentos_clinicos",
        verbose_name="Médico",
    )
    data_prevista = models.DateField("Data prevista")
    motivo = models.CharField("Motivo", max_length=255)
    observacoes = models.TextField("Observações", blank=True)
    consulta_agendada = models.ForeignKey(
        "appointments.Appointment",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="seguimento_clinico_origem",
        verbose_name="Consulta agendada",
    )

    class Meta:
        verbose_name = "Seguimento clínico"
        verbose_name_plural = "Seguimentos clínicos"
        ordering = ["-data_prevista"]
