"""Signals do módulo de pacientes."""

from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.patients.constants import HistoryEventType
from apps.patients.models import PatientAllergy, PatientChronicDisease, PatientDocument, PatientObservation
from apps.patients.services.history_service import PatientHistoryService


@receiver(post_save, sender=PatientAllergy)
def allergy_history(sender, instance, created, **kwargs):
    if not created:
        return
    PatientHistoryService.record(
        patient=instance.patient,
        event_type=HistoryEventType.ALERGIA,
        title="Alergia registada",
        description=f"{instance.allergen} — {instance.get_severity_display()}",
        user=instance.recorded_by,
        source_id=instance.pk,
        metadata={"allergy_id": instance.pk, "severity": instance.severity},
    )


@receiver(post_save, sender=PatientChronicDisease)
def chronic_disease_history(sender, instance, created, **kwargs):
    if not created:
        return
    PatientHistoryService.record(
        patient=instance.patient,
        event_type=HistoryEventType.DOENCA_CRONICA,
        title="Doença crónica registada",
        description=instance.disease_name,
        user=instance.recorded_by,
        source_id=instance.pk,
        metadata={"chronic_disease_id": instance.pk},
    )


@receiver(post_save, sender=PatientDocument)
def document_history(sender, instance, created, **kwargs):
    if not created:
        return
    PatientHistoryService.record(
        patient=instance.patient,
        event_type=HistoryEventType.DOCUMENTO,
        title="Documento carregado",
        description=instance.title,
        user=instance.uploaded_by,
        source_id=instance.pk,
        metadata={"document_id": instance.pk, "document_type": instance.document_type},
    )


@receiver(post_save, sender=PatientObservation)
def observation_history(sender, instance, created, **kwargs):
    if not created:
        return
    PatientHistoryService.record(
        patient=instance.patient,
        event_type=HistoryEventType.OBSERVACAO,
        title="Observação registada",
        description=instance.content[:200],
        user=instance.created_by,
        source_id=instance.pk,
        metadata={"observation_id": instance.pk, "observation_type": instance.observation_type},
    )
