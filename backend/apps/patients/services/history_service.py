"""Registo de histórico clínico do paciente."""

from django.utils import timezone

from apps.patients.constants import HistoryEventType
from apps.patients.models import PatientHistory


class PatientHistoryService:
    @staticmethod
    def record(
        patient,
        event_type: str,
        title: str,
        description: str = "",
        user=None,
        source_module: str = "patients",
        source_id: int | None = None,
        metadata: dict | None = None,
        event_date=None,
    ) -> PatientHistory:
        return PatientHistory.objects.create(
            patient=patient,
            event_type=event_type,
            title=title,
            description=description,
            event_date=event_date or timezone.now(),
            source_module=source_module,
            source_id=source_id,
            metadata=metadata or {},
            recorded_by=user,
        )

    @staticmethod
    def record_registration(patient, user=None) -> PatientHistory:
        return PatientHistoryService.record(
            patient=patient,
            event_type=HistoryEventType.REGISTO,
            title="Paciente registado",
            description=f"Registo inicial — nº {patient.patient_number}.",
            user=user,
            source_id=patient.pk,
        )
