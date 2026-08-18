"""Resolução determinística de duplicados (alias, sem apagar histórico)."""

from __future__ import annotations

from apps.data_migration.constants import PATIENT_REVIEW_MERGE
from apps.patients.constants import HistoryEventType
from apps.patients.models import Patient
from apps.patients.services.history_service import PatientHistoryService


def canonical_migration_id(left: str, right: str) -> str:
    ids = sorted(item.strip() for item in (left, right) if (item or "").strip())
    return ids[0] if ids else ""


def alias_migration_id(left: str, right: str) -> str:
    canonical = canonical_migration_id(left, right)
    ids = {item.strip() for item in (left, right) if (item or "").strip()}
    ids.discard(canonical)
    return next(iter(ids), "")


def pair_ids(pair: dict[str, str]) -> tuple[str, str]:
    left = (pair.get("paciente_a_id") or pair.get("paciente_a") or pair.get("id_a") or "").strip()
    right = (pair.get("paciente_b_id") or pair.get("paciente_b") or "").strip()
    return left, right


def alias_map_from_pairs(pairs: list[dict[str, str]]) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for pair in pairs:
        if (pair.get("decisao") or "").strip().upper() != PATIENT_REVIEW_MERGE:
            continue
        left, right = pair_ids(pair)
        canonical = canonical_migration_id(left, right)
        alias = alias_migration_id(left, right)
        if canonical and alias:
            mapping[alias] = canonical
    return mapping


def resolve_patient_id(migration_id: str, alias_map: dict[str, str]) -> str:
    current = (migration_id or "").strip()
    seen: set[str] = set()
    while current in alias_map and current not in seen:
        seen.add(current)
        current = alias_map[current]
    return current


def record_alias(
    canonical: Patient,
    *,
    alias_migration_id_value: str,
    grupo: str,
    actor,
    batch_id: str,
) -> Patient:
    """Regista alias no paciente canónico. Não apaga o alias nem o histórico."""
    meta = dict(canonical.metadata or {})
    original_mid = meta.get("migration_id") or ""
    aliases = [item for item in (meta.get("historical_aliases") or []) if item]
    if alias_migration_id_value and alias_migration_id_value not in aliases:
        aliases.append(alias_migration_id_value)
    decisions = list(meta.get("duplicate_decisions") or [])
    decisions.append(
        {
            "grupo": grupo,
            "decisao": PATIENT_REVIEW_MERGE,
            "canonical_migration_id": original_mid,
            "alias_migration_id": alias_migration_id_value,
            "actor": getattr(actor, "email", "") or "",
            "import_batch": batch_id,
        }
    )
    meta["historical_aliases"] = aliases
    meta["duplicate_decisions"] = decisions
    meta["migration_id"] = original_mid
    canonical.metadata = meta
    canonical.updated_by = actor
    canonical.save(update_fields=["metadata", "updated_by", "updated_at"])
    PatientHistoryService.record(
        canonical,
        event_type=HistoryEventType.OBSERVACAO,
        title="Alias histórico confirmado (MESMA_PESSOA)",
        description="O identificador histórico adicional ficou associado a este utente. Histórico não foi apagado.",
        user=actor,
        source_module=meta.get("source") or "MIGRACAO_EXCEL_SAUVIDA",
        metadata={
            "source": meta.get("source"),
            "import_batch": batch_id,
            "migration_id": original_mid,
            "alias_migration_id": alias_migration_id_value,
            "grupo": grupo,
            "record_class": meta.get("record_class"),
        },
    )
    return canonical


def mark_alias_patient(alias_patient: Patient, *, canonical_migration_id_value: str, actor, batch_id: str) -> Patient:
    """Desactiva o duplicado importado sem o apagar."""
    meta = dict(alias_patient.metadata or {})
    meta["merged_into_migration_id"] = canonical_migration_id_value
    meta["verification_state"] = "ALIAS_MESMA_PESSOA"
    meta["import_batch_alias"] = batch_id
    alias_patient.metadata = meta
    alias_patient.is_active = False
    alias_patient.updated_by = actor
    alias_patient.save(update_fields=["metadata", "is_active", "updated_by", "updated_at"])
    return alias_patient


alias_map_from_pairs = alias_map_from_pairs
canonical_migration_id = canonical_migration_id
resolve_patient_id = resolve_patient_id
record_alias = record_alias
mark_alias_patient = mark_alias_patient
pair_ids = pair_ids
