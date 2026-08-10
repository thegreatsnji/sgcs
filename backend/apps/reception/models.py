"""Modelos do módulo de receção."""

from django.conf import settings
from django.db import models

from apps.reception.constants import (
    CheckInStatus,
    PatientAgeCategory,
    QueuePriority,
    QueueStatus,
    ReferralDepartment,
    TriageColor,
    VisitPurpose,
)
from core.mixins import TimestampMixin


class ReceptionCheckIn(TimestampMixin):
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.PROTECT,
        related_name="reception_check_ins",
        verbose_name="Paciente",
    )
    receptionist = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="reception_check_ins",
        verbose_name="Rececionista",
    )
    check_in_time = models.DateTimeField("Hora de check-in", auto_now_add=True)
    status = models.CharField(
        "Estado",
        max_length=20,
        choices=CheckInStatus.choices,
        default=CheckInStatus.WAITING,
    )
    priority = models.CharField(
        "Prioridade",
        max_length=20,
        choices=QueuePriority.choices,
        default=QueuePriority.NORMAL,
    )
    triage_color = models.CharField(
        "Cor de triagem",
        max_length=10,
        choices=TriageColor.choices,
        blank=True,
    )
    age_at_check_in = models.PositiveSmallIntegerField("Idade na triagem", null=True, blank=True)
    age_category_at_check_in = models.CharField(
        "Categoria etária na triagem",
        max_length=10,
        choices=PatientAgeCategory.choices,
        blank=True,
    )
    weight = models.DecimalField("Peso (kg)", max_digits=5, decimal_places=2, null=True, blank=True)
    temperature = models.DecimalField(
        "Temperatura (°C)",
        max_digits=4,
        decimal_places=1,
        null=True,
        blank=True,
    )
    blood_pressure = models.CharField("Pressão arterial", max_length=20, blank=True)
    height_cm = models.PositiveSmallIntegerField("Altura (cm)", null=True, blank=True)
    spo2 = models.PositiveSmallIntegerField("SpO₂ (%)", null=True, blank=True)
    heart_rate = models.PositiveSmallIntegerField("FC (b/min)", null=True, blank=True)
    respiratory_rate = models.PositiveSmallIntegerField("FR (c/min)", null=True, blank=True)
    race = models.CharField("Raça", max_length=80, blank=True)
    visit_purpose = models.CharField(
        "Motivo da visita",
        max_length=12,
        choices=VisitPurpose.choices,
        default=VisitPurpose.CONSULTA,
        blank=True,
    )
    symptoms = models.TextField("Sintomas", blank=True)
    notes = models.TextField("Notas", blank=True)

    class Meta:
        verbose_name = "Check-in"
        verbose_name_plural = "Check-ins"
        ordering = ["-check_in_time"]
        indexes = [
            models.Index(fields=["status", "check_in_time"], name="idx_checkin_status_time"),
            models.Index(fields=["patient", "status"], name="idx_checkin_patient_status"),
            models.Index(fields=["priority"], name="idx_checkin_priority"),
        ]

    def __str__(self) -> str:
        return f"{self.patient.full_name} — {self.get_status_display()}"


class WaitingQueue(TimestampMixin):
    check_in = models.OneToOneField(
        ReceptionCheckIn,
        on_delete=models.CASCADE,
        related_name="queue_entry",
        verbose_name="Check-in",
    )
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.PROTECT,
        related_name="queue_entries",
        verbose_name="Paciente",
    )
    position = models.PositiveIntegerField("Posição")
    estimated_wait_minutes = models.PositiveIntegerField(
        "Tempo estimado (min)",
        null=True,
        blank=True,
    )
    status = models.CharField(
        "Estado",
        max_length=20,
        choices=QueueStatus.choices,
        default=QueueStatus.WAITING,
    )

    class Meta:
        verbose_name = "Fila de espera"
        verbose_name_plural = "Fila de espera"
        ordering = ["position", "created_at"]
        indexes = [
            models.Index(fields=["status", "position"], name="idx_queue_status_position"),
            models.Index(fields=["patient", "status"], name="idx_queue_patient_status"),
        ]

    def __str__(self) -> str:
        return f"#{self.position} — {self.patient.full_name}"


class Referral(TimestampMixin):
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.PROTECT,
        related_name="referrals",
        verbose_name="Paciente",
    )
    check_in = models.ForeignKey(
        ReceptionCheckIn,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="referrals",
        verbose_name="Check-in",
    )
    from_department = models.CharField(
        "Departamento origem",
        max_length=20,
        choices=ReferralDepartment.choices,
        default=ReferralDepartment.RECEPTION,
    )
    to_department = models.CharField(
        "Departamento destino",
        max_length=20,
        choices=ReferralDepartment.choices,
    )
    reason = models.TextField("Motivo")
    referred_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="referrals_created",
        verbose_name="Encaminhado por",
    )
    assigned_doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="referrals_assigned",
        verbose_name="Médico atribuído",
    )

    class Meta:
        verbose_name = "Encaminhamento"
        verbose_name_plural = "Encaminhamentos"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["patient", "created_at"], name="idx_referral_patient_date"),
            models.Index(fields=["to_department"], name="idx_referral_to_dept"),
        ]

    def __str__(self) -> str:
        return f"{self.patient.full_name} → {self.get_to_department_display()}"
