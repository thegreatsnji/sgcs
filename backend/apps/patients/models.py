"""Modelos do módulo de pacientes."""

from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.patients.constants import (
    AllergySeverity,
    BloodType,
    ChronicDiseaseStatus,
    DocumentType,
    EmergencyRelationship,
    HistoryEventType,
    InsurancePlanType,
    MaritalStatus,
    ObservationType,
    PatientDocumentType,
    PatientGender,
)
from core.mixins import SoftDeleteMixin, TimestampMixin


class Patient(TimestampMixin, SoftDeleteMixin, models.Model):
    patient_number = models.CharField("Nº processo", max_length=20, unique=True, editable=False)
    first_name = models.CharField("Nome", max_length=100)
    last_name = models.CharField("Apelido", max_length=100)
    full_name = models.CharField("Nome completo", max_length=201, editable=False)
    document_type = models.CharField(
        "Tipo de documento",
        max_length=20,
        choices=DocumentType.choices,
        blank=True,
    )
    document_number = models.CharField("Nº documento", max_length=50, blank=True)
    birth_date = models.DateField("Data de nascimento")
    gender = models.CharField("Sexo", max_length=1, choices=PatientGender.choices)
    phone = models.CharField("Telefone", max_length=20)
    email = models.EmailField("E-mail", blank=True)
    address_street = models.CharField("Morada", max_length=255, blank=True)
    address_city = models.CharField("Cidade", max_length=100, blank=True)
    address_region = models.CharField("Região", max_length=100, blank=True)
    address_country = models.CharField("País", max_length=100, blank=True, default="Guiné-Bissau")
    address_postal_code = models.CharField("Código postal", max_length=20, blank=True)
    nationality = models.CharField("Nacionalidade", max_length=100, blank=True)
    blood_type = models.CharField(
        "Grupo sanguíneo",
        max_length=12,
        choices=BloodType.choices,
        blank=True,
    )
    marital_status = models.CharField(
        "Estado civil",
        max_length=20,
        choices=MaritalStatus.choices,
        blank=True,
    )
    occupation = models.CharField("Profissão", max_length=150, blank=True)
    is_active = models.BooleanField("Ativo", default=True)
    deleted_at = models.DateTimeField("Eliminado em", null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="patients_created",
        verbose_name="Criado por",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="patients_updated",
        verbose_name="Atualizado por",
    )

    class Meta:
        verbose_name = "Paciente"
        verbose_name_plural = "Pacientes"
        ordering = ["last_name", "first_name"]
        indexes = [
            models.Index(fields=["last_name", "first_name"], name="idx_patient_last_first"),
            models.Index(fields=["full_name"], name="idx_patient_full_name"),
            models.Index(fields=["document_number"], name="idx_patient_document"),
            models.Index(fields=["phone"], name="idx_patient_phone"),
            models.Index(fields=["patient_number"], name="idx_patient_number"),
            models.Index(fields=["is_active", "is_deleted"], name="idx_patient_active_del"),
            models.Index(fields=["birth_date"], name="idx_patient_birth_date"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["document_number"],
                condition=models.Q(document_number__gt=""),
                name="patients_patient_unique_document",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.full_name} ({self.patient_number})"

    def save(self, *args, **kwargs):
        self.full_name = f"{self.first_name} {self.last_name}".strip()
        super().save(*args, **kwargs)

    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.is_active = False
        self.save(update_fields=["is_deleted", "deleted_at", "is_active", "updated_at"])

    def restore(self):
        self.is_deleted = False
        self.deleted_at = None
        self.is_active = True
        self.save(update_fields=["is_deleted", "deleted_at", "is_active", "updated_at"])

    @property
    def age(self) -> int:
        today = timezone.localdate()
        years = today.year - self.birth_date.year
        if (today.month, today.day) < (self.birth_date.month, self.birth_date.day):
            years -= 1
        return years


class PatientEmergencyContact(TimestampMixin, models.Model):
    patient = models.ForeignKey(
        Patient,
        on_delete=models.RESTRICT,
        related_name="emergency_contacts",
        verbose_name="Paciente",
    )
    name = models.CharField("Nome", max_length=150)
    phone = models.CharField("Telefone", max_length=20)
    email = models.EmailField("E-mail", blank=True)
    relationship = models.CharField(
        "Parentesco",
        max_length=50,
        choices=EmergencyRelationship.choices,
    )
    is_primary = models.BooleanField("Principal", default=False)
    is_active = models.BooleanField("Ativo", default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="emergency_contacts_created",
    )

    class Meta:
        verbose_name = "Contacto de emergência"
        verbose_name_plural = "Contactos de emergência"
        ordering = ["-is_primary", "name"]
        indexes = [
            models.Index(fields=["patient", "is_primary"], name="idx_emerg_patient_primary"),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.patient_id})"


class PatientInsurance(TimestampMixin, models.Model):
    patient = models.ForeignKey(
        Patient,
        on_delete=models.RESTRICT,
        related_name="insurances",
        verbose_name="Paciente",
    )
    provider_name = models.CharField("Seguradora", max_length=150)
    policy_number = models.CharField("Nº apólice", max_length=50)
    plan_type = models.CharField(
        "Tipo de plano",
        max_length=50,
        choices=InsurancePlanType.choices,
        blank=True,
    )
    valid_from = models.DateField("Válido de", null=True, blank=True)
    valid_until = models.DateField("Válido até", null=True, blank=True)
    is_primary = models.BooleanField("Principal", default=False)
    is_active = models.BooleanField("Ativo", default=True)
    notes = models.TextField("Notas", blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="patient_insurances_created",
    )

    class Meta:
        verbose_name = "Seguro"
        verbose_name_plural = "Seguros"
        ordering = ["-is_primary", "-valid_from"]
        indexes = [
            models.Index(fields=["patient", "is_active"], name="idx_insurance_patient_active"),
            models.Index(fields=["policy_number"], name="idx_insurance_policy"),
        ]

    def __str__(self) -> str:
        return f"{self.provider_name} — {self.policy_number}"


class PatientAllergy(TimestampMixin, models.Model):
    patient = models.ForeignKey(
        Patient,
        on_delete=models.RESTRICT,
        related_name="allergies",
        verbose_name="Paciente",
    )
    allergen = models.CharField("Alergénio", max_length=150)
    severity = models.CharField(
        "Gravidade",
        max_length=20,
        choices=AllergySeverity.choices,
        default=AllergySeverity.MODERADA,
    )
    reaction = models.CharField("Reação", max_length=255, blank=True)
    diagnosed_at = models.DateField("Diagnosticado em", null=True, blank=True)
    is_active = models.BooleanField("Ativo", default=True)
    notes = models.TextField("Notas", blank=True)
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="patient_allergies_recorded",
    )

    class Meta:
        verbose_name = "Alergia"
        verbose_name_plural = "Alergias"
        ordering = ["-severity", "allergen"]
        indexes = [
            models.Index(fields=["patient"], name="idx_allergy_patient"),
            models.Index(fields=["allergen"], name="idx_allergy_allergen"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["patient", "allergen"],
                condition=models.Q(is_active=True),
                name="uniq_patient_allergen_active",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.allergen} ({self.severity})"


class PatientChronicDisease(TimestampMixin, models.Model):
    patient = models.ForeignKey(
        Patient,
        on_delete=models.RESTRICT,
        related_name="chronic_diseases",
        verbose_name="Paciente",
    )
    disease_name = models.CharField("Doença", max_length=200)
    icd_code = models.CharField("Código CID", max_length=20, blank=True)
    diagnosed_at = models.DateField("Diagnosticado em", null=True, blank=True)
    status = models.CharField(
        "Estado",
        max_length=20,
        choices=ChronicDiseaseStatus.choices,
        default=ChronicDiseaseStatus.ATIVA,
    )
    is_active = models.BooleanField("Ativo", default=True)
    notes = models.TextField("Notas", blank=True)
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="chronic_diseases_recorded",
    )

    class Meta:
        verbose_name = "Doença crónica"
        verbose_name_plural = "Doenças crónicas"
        ordering = ["disease_name"]
        indexes = [
            models.Index(fields=["patient"], name="idx_chronic_patient"),
            models.Index(fields=["icd_code"], name="idx_chronic_icd"),
        ]

    def __str__(self) -> str:
        return self.disease_name


class PatientDocument(TimestampMixin, models.Model):
    patient = models.ForeignKey(
        Patient,
        on_delete=models.RESTRICT,
        related_name="documents",
        verbose_name="Paciente",
    )
    stored_file = models.ForeignKey(
        "files.StoredFile",
        on_delete=models.RESTRICT,
        related_name="patient_documents",
        verbose_name="Ficheiro",
    )
    document_type = models.CharField(
        "Tipo",
        max_length=30,
        choices=PatientDocumentType.choices,
    )
    title = models.CharField("Título", max_length=200)
    document_number = models.CharField("Nº documento", max_length=50, blank=True)
    description = models.TextField("Descrição", blank=True)
    issued_at = models.DateField("Emitido em", null=True, blank=True)
    expires_at = models.DateField("Validade", null=True, blank=True)
    is_active = models.BooleanField("Ativo", default=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="patient_documents_uploaded",
    )

    class Meta:
        verbose_name = "Documento"
        verbose_name_plural = "Documentos"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["patient", "document_type"], name="idx_doc_patient_type"),
        ]

    def __str__(self) -> str:
        return self.title


class PatientPhoto(TimestampMixin, models.Model):
    patient = models.ForeignKey(
        Patient,
        on_delete=models.RESTRICT,
        related_name="photos",
        verbose_name="Paciente",
    )
    stored_file = models.ForeignKey(
        "files.StoredFile",
        on_delete=models.RESTRICT,
        related_name="patient_photos",
        verbose_name="Imagem",
    )
    is_primary = models.BooleanField("Principal", default=False)
    caption = models.CharField("Legenda", max_length=255, blank=True)
    taken_at = models.DateTimeField("Data da foto", null=True, blank=True)
    is_active = models.BooleanField("Ativo", default=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="patient_photos_uploaded",
    )

    class Meta:
        verbose_name = "Fotografia"
        verbose_name_plural = "Fotografias"
        ordering = ["-is_primary", "-created_at"]
        indexes = [
            models.Index(fields=["patient", "is_primary"], name="idx_photo_patient_primary"),
        ]

    def __str__(self) -> str:
        return f"Foto {self.patient_id} — {self.pk}"


class PatientHistory(models.Model):
    patient = models.ForeignKey(
        Patient,
        on_delete=models.RESTRICT,
        related_name="history_entries",
        verbose_name="Paciente",
    )
    event_type = models.CharField(
        "Tipo de evento",
        max_length=30,
        choices=HistoryEventType.choices,
    )
    title = models.CharField("Título", max_length=200)
    description = models.TextField("Descrição", blank=True)
    event_date = models.DateTimeField("Data do evento")
    source_module = models.CharField("Módulo de origem", max_length=30, blank=True)
    source_id = models.BigIntegerField("ID de origem", null=True, blank=True)
    metadata = models.JSONField("Metadados", default=dict, blank=True)
    created_at = models.DateTimeField("Registado em", auto_now_add=True)
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="patient_history_recorded",
    )

    class Meta:
        verbose_name = "Histórico"
        verbose_name_plural = "Históricos"
        ordering = ["-event_date"]
        indexes = [
            models.Index(fields=["patient", "event_date"], name="idx_history_patient_date"),
            models.Index(fields=["event_type"], name="idx_history_event_type"),
            models.Index(fields=["source_module", "source_id"], name="idx_history_source"),
        ]

    def __str__(self) -> str:
        return f"{self.event_type} — {self.title}"


class PatientObservation(TimestampMixin, models.Model):
    patient = models.ForeignKey(
        Patient,
        on_delete=models.RESTRICT,
        related_name="observations",
        verbose_name="Paciente",
    )
    observation_type = models.CharField(
        "Tipo",
        max_length=20,
        choices=ObservationType.choices,
    )
    content = models.TextField("Conteúdo")
    is_pinned = models.BooleanField("Fixada", default=False)
    is_active = models.BooleanField("Ativo", default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="patient_observations_created",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="patient_observations_updated",
    )

    class Meta:
        verbose_name = "Observação"
        verbose_name_plural = "Observações"
        ordering = ["-is_pinned", "-created_at"]
        indexes = [
            models.Index(fields=["patient", "is_pinned"], name="idx_obs_patient_pinned"),
            models.Index(fields=["observation_type"], name="idx_obs_type"),
        ]

    def __str__(self) -> str:
        return f"{self.observation_type} — {self.patient_id}"
