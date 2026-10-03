"""Rollback por lote da migração histórica SauVida."""

from __future__ import annotations

from django.db import transaction

from apps.data_migration.constants import FONTE_MIGRACAO
from apps.patients.constants import HistoryEventType
from apps.patients.models import Patient, PatientHistory
from apps.patients.services.dependency_service import PatientDependencyService


def _history_breakdown(histories) -> dict:
    registo = histories.filter(event_type=HistoryEventType.REGISTO)
    clinical = histories.exclude(event_type=HistoryEventType.REGISTO)
    finance = histories.filter(metadata__kind="REGISTO_FINANCEIRO_HISTORICO")
    foreign = 0
    for row in histories.select_related("patient"):
        meta = row.patient.metadata if isinstance(row.patient.metadata, dict) else {}
        if meta.get("import_batch") != (row.metadata or {}).get("import_batch") and meta.get("source") != FONTE_MIGRACAO:
            foreign += 1
    return {
        "historicos_registo_importacao": registo.count(),
        "historicos_clinicos": clinical.count(),
        "historicos_financeiros_extra": finance.count(),
        "historicos_em_pacientes_externos": foreign,
    }


def rollback_batch(batch_id: str, *, apply: bool = False) -> dict:
    histories = PatientHistory.objects.filter(
        source_module=FONTE_MIGRACAO,
        metadata__import_batch=batch_id,
    )
    patients = Patient.objects.filter(
        metadata__source=FONTE_MIGRACAO,
        metadata__import_batch=batch_id,
        is_deleted=False,
    )
    history_count = histories.count()
    patient_count = patients.count()
    skipped_patients = 0
    deleted_patients = 0
    deleted_histories = 0
    breakdown = _history_breakdown(histories)

    if not apply:
        return {
            "import_batch": batch_id,
            "apply": False,
            "historicos_a_remover": history_count,
            "pacientes_a_remover": patient_count,
            "pacientes_preservados": 0,
            "escrita_bd": False,
            **breakdown,
        }

    with transaction.atomic():
        deleted_histories, _ = histories.delete()
        for patient in list(patients):
            deps = PatientDependencyService.get_blocking_dependencies(patient.pk)
            leftover = PatientHistory.objects.filter(patient=patient).exclude(
                source_module=FONTE_MIGRACAO,
                metadata__import_batch=batch_id,
            )
            if deps or leftover.exists():
                skipped_patients += 1
                continue
            patient.delete()
            deleted_patients += 1

    return {
        "import_batch": batch_id,
        "apply": True,
        "historicos_removidos": deleted_histories,
        "pacientes_removidos": deleted_patients,
        "pacientes_preservados": skipped_patients,
        "escrita_bd": True,
        **breakdown,
    }
