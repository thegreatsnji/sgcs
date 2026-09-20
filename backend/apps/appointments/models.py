"""Modelos do módulo de consultas."""

from django.conf import settings
from django.db import models

from apps.appointments.constants import (
    AppointmentStatus,
    DEFAULT_DURATION_MINUTES,
    DiagnosticoTipo,
    PedidoEstado,
    PedidoLaboratorioEstadoFaturacao,
)
from apps.reception.constants import QueuePriority
from core.mixins import TimestampMixin


class Appointment(TimestampMixin):
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.PROTECT,
        related_name="appointments",
        verbose_name="Paciente",
    )
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="appointments",
        verbose_name="Médico",
    )
    receptionist = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="appointments_receptionist",
        verbose_name="Rececionista",
    )
    queue_entry = models.ForeignKey(
        "reception.WaitingQueue",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="appointments",
        verbose_name="Entrada na fila",
    )
    check_in = models.ForeignKey(
        "reception.ReceptionCheckIn",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="appointments",
        verbose_name="Check-in",
    )
    referral = models.ForeignKey(
        "reception.Referral",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="appointments",
        verbose_name="Encaminhamento",
    )
    appointment_number = models.CharField(
        "Número da consulta",
        max_length=20,
        unique=True,
        blank=True,
    )
    scheduled_at = models.DateTimeField("Data/hora da consulta")
    consultation_date = models.DateField("Data da consulta", null=True, blank=True)
    started_at = models.DateTimeField("Hora de início", null=True, blank=True)
    completed_at = models.DateTimeField("Hora de fim", null=True, blank=True)
    duration_minutes = models.PositiveIntegerField(
        "Duração (min)",
        default=DEFAULT_DURATION_MINUTES,
    )
    status = models.CharField(
        "Estado",
        max_length=20,
        choices=AppointmentStatus.choices,
        default=AppointmentStatus.AGENDADA,
    )
    priority = models.CharField(
        "Prioridade",
        max_length=20,
        choices=QueuePriority.choices,
        default=QueuePriority.NORMAL,
    )
    chief_complaint = models.TextField("Motivo da consulta", blank=True)
    notes = models.TextField("Observações", blank=True)
    diagnosis = models.TextField("Diagnóstico", blank=True)
    clinical_notes = models.TextField("Notas clínicas", blank=True)
    cancellation_reason = models.TextField("Motivo de cancelamento", blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="appointments_created",
        verbose_name="Criado por",
    )

    class Meta:
        verbose_name = "Consulta"
        verbose_name_plural = "Consultas"
        ordering = ["-scheduled_at"]
        indexes = [
            models.Index(fields=["patient", "scheduled_at"], name="idx_appt_patient_date"),
            models.Index(fields=["patient", "status"], name="idx_appt_patient_status"),
            models.Index(fields=["doctor", "status"], name="idx_appt_doctor_status"),
            models.Index(fields=["status", "scheduled_at"], name="idx_appt_status_date"),
            models.Index(fields=["consultation_date", "doctor"], name="idx_appt_date_doctor"),
            models.Index(fields=["appointment_number"], name="idx_appt_number"),
        ]

    def __str__(self) -> str:
        label = self.appointment_number or f"#{self.pk}"
        return f"{label} — {self.patient.full_name} — {self.get_status_display()}"

    def save(self, *args, **kwargs):
        if self.scheduled_at and not self.consultation_date:
            self.consultation_date = self.scheduled_at.date()
        super().save(*args, **kwargs)

    @property
    def is_clinical_editable(self) -> bool:
        return self.status == AppointmentStatus.EM_CONSULTA


class SinaisVitais(TimestampMixin):
    consulta = models.OneToOneField(
        Appointment,
        on_delete=models.CASCADE,
        related_name="sinais_vitais",
        verbose_name="Consulta",
    )
    pressao_arterial = models.CharField("Pressão arterial", max_length=20, blank=True)
    frequencia_cardiaca = models.PositiveSmallIntegerField(
        "Frequência cardíaca (bpm)",
        null=True,
        blank=True,
    )
    frequencia_respiratoria = models.PositiveSmallIntegerField(
        "Frequência respiratória (rpm)",
        null=True,
        blank=True,
    )
    temperatura = models.DecimalField(
        "Temperatura (°C)",
        max_digits=4,
        decimal_places=1,
        null=True,
        blank=True,
    )
    saturacao_oxigenio = models.PositiveSmallIntegerField(
        "Saturação de oxigénio (%)",
        null=True,
        blank=True,
    )
    peso = models.DecimalField("Peso (kg)", max_digits=6, decimal_places=2, null=True, blank=True)
    altura = models.DecimalField("Altura (cm)", max_digits=5, decimal_places=1, null=True, blank=True)
    imc = models.DecimalField("IMC", max_digits=5, decimal_places=2, null=True, blank=True)
    observacoes = models.TextField("Observações", blank=True)
    registado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sinais_vitais_registados",
        verbose_name="Registado por",
    )

    class Meta:
        verbose_name = "Sinais vitais"
        verbose_name_plural = "Sinais vitais"

    def save(self, *args, **kwargs):
        if self.peso and self.altura and self.altura > 0:
            altura_m = float(self.altura) / 100
            self.imc = round(float(self.peso) / (altura_m**2), 2)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"Sinais vitais — {self.consulta}"


class AnotacaoClinica(TimestampMixin):
    consulta = models.OneToOneField(
        Appointment,
        on_delete=models.CASCADE,
        related_name="anotacao_soap",
        verbose_name="Consulta",
    )
    subjetivo = models.TextField("Subjetivo (S)", blank=True)
    objetivo = models.TextField("Objetivo (O)", blank=True)
    avaliacao = models.TextField("Avaliação (A)", blank=True)
    plano = models.TextField("Plano (P)", blank=True)
    registado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="anotacoes_clinicas",
        verbose_name="Registado por",
    )

    class Meta:
        verbose_name = "Anotação clínica (SOAP)"
        verbose_name_plural = "Anotações clínicas (SOAP)"

    def __str__(self) -> str:
        return f"SOAP — {self.consulta}"


class Diagnostico(TimestampMixin):
    consulta = models.ForeignKey(
        Appointment,
        on_delete=models.CASCADE,
        related_name="diagnosticos",
        verbose_name="Consulta",
    )
    codigo_cid10 = models.CharField("Código CID-10", max_length=20)
    descricao = models.CharField("Descrição", max_length=255)
    tipo = models.CharField(
        "Tipo",
        max_length=20,
        choices=DiagnosticoTipo.choices,
        default=DiagnosticoTipo.PRINCIPAL,
    )
    registado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="diagnosticos_registados",
        verbose_name="Registado por",
    )

    class Meta:
        verbose_name = "Diagnóstico"
        verbose_name_plural = "Diagnósticos"
        ordering = ["tipo", "id"]

    def __str__(self) -> str:
        return f"{self.codigo_cid10} — {self.descricao}"


class PedidoLaboratorio(TimestampMixin):
    consulta = models.ForeignKey(
        Appointment,
        on_delete=models.CASCADE,
        related_name="pedidos_laboratorio",
        verbose_name="Consulta",
    )
    tipo_exame = models.CharField("Tipo de exame", max_length=150)
    servico = models.ForeignKey(
        "billing.Servico",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="pedidos_laboratorio_clinicos",
        verbose_name="Serviço",
    )
    estado_faturacao = models.CharField(
        "Estado de faturação",
        max_length=30,
        choices=PedidoLaboratorioEstadoFaturacao.choices,
        default=PedidoLaboratorioEstadoFaturacao.AGUARDA_REGULARIZACAO,
    )
    prioridade = models.CharField(
        "Prioridade",
        max_length=20,
        choices=QueuePriority.choices,
        default=QueuePriority.NORMAL,
    )
    observacoes = models.TextField("Observações", blank=True)
    estado = models.CharField(
        "Estado",
        max_length=20,
        choices=PedidoEstado.choices,
        default=PedidoEstado.PENDENTE,
    )
    solicitado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="pedidos_laboratorio_solicitados",
        verbose_name="Solicitado por",
    )

    class Meta:
        verbose_name = "Pedido de laboratório"
        verbose_name_plural = "Pedidos de laboratório"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.tipo_exame} — {self.consulta}"


class PedidoImagiologia(TimestampMixin):
    consulta = models.ForeignKey(
        Appointment,
        on_delete=models.CASCADE,
        related_name="pedidos_imagiologia",
        verbose_name="Consulta",
    )
    tipo_exame = models.CharField("Tipo de exame", max_length=150)
    prioridade = models.CharField(
        "Prioridade",
        max_length=20,
        choices=QueuePriority.choices,
        default=QueuePriority.NORMAL,
    )
    observacoes = models.TextField("Observações", blank=True)
    estado = models.CharField(
        "Estado",
        max_length=20,
        choices=PedidoEstado.choices,
        default=PedidoEstado.PENDENTE,
    )
    solicitado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="pedidos_imagiologia_solicitados",
        verbose_name="Solicitado por",
    )

    class Meta:
        verbose_name = "Pedido de imagiologia"
        verbose_name_plural = "Pedidos de imagiologia"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.tipo_exame} — {self.consulta}"


class Seguimento(TimestampMixin):
    consulta = models.OneToOneField(
        Appointment,
        on_delete=models.CASCADE,
        related_name="seguimento",
        verbose_name="Consulta",
    )
    data_retorno = models.DateField("Data de retorno")
    motivo = models.CharField("Motivo", max_length=255)
    observacoes = models.TextField("Observações", blank=True)
    registado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="seguimentos_registados",
        verbose_name="Registado por",
    )

    class Meta:
        verbose_name = "Seguimento"
        verbose_name_plural = "Seguimentos"

    def __str__(self) -> str:
        return f"Retorno {self.data_retorno:%d/%m/%Y} — {self.consulta}"
