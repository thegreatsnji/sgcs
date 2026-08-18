"""Classificação de eventos bloqueados (sem PII nos agregados)."""

from __future__ import annotations

from collections import Counter
from typing import Any

REASON_ORDER = (
    "DATA_SUSPEITA",
    "LAB_AMBIGUO",
    "PACIENTE_DUPLICADO",
    "SEM_DATA",
    "OUTRO",
)

PATIENT_BLOCK_REASONS = {"PACIENTE_DUPLICADO", "PACIENTE_BLOQUEADO"}
DATE_MISSING_REASONS = {"SEM_DATA", "DESCRICAO_INSUFICIENTE"}


def event_block_reasons(
    event: dict[str, str],
    *,
    blocked_patients: set[str],
    date_decision: dict[str, dict[str, str]],
) -> list[str]:
    reasons: list[str] = []
    hid = (event.get("historico_id") or "").strip()
    pid = (event.get("migration_patient_id") or "").strip()
    if pid in blocked_patients:
        reasons.append("PACIENTE_DUPLICADO")
    date_row = date_decision.get(hid)
    if date_row is not None:
        decision = (date_row.get("decisao") or "").strip().upper()
        if decision not in {"ACEITAR", "CONFIRMADA", "OK", "CONFIRMAR_DATA", "CORRIGIR_DATA"}:
            reasons.append("DATA_SUSPEITA")
    if (event.get("tipo_evento") or "") == "LABORATORIO" and (event.get("estado_mapeamento") or "") == "AMBIGUO":
        reasons.append("LAB_AMBIGUO")
    if not event.get("data_evento") and hid not in date_decision:
        reasons.append("SEM_DATA")
    return reasons or ["OUTRO"]


def primary_block_reason(reasons: list[str]) -> str:
    ranked = [reason for reason in REASON_ORDER if reason in reasons]
    return ranked[0] if ranked else "OUTRO"


def classify_blocked_events(
    blocked_events: list[dict[str, str]],
    *,
    blocked_patients: set[str],
    date_decision: dict[str, dict[str, str]],
) -> dict[str, Any]:
    counts: Counter[str] = Counter()
    only_patient = 0
    annotated: list[dict[str, str]] = []
    for event in blocked_events:
        reasons = event_block_reasons(
            event, blocked_patients=blocked_patients, date_decision=date_decision
        )
        primary = primary_block_reason(reasons)
        counts[primary] += 1
        if reasons == ["PACIENTE_DUPLICADO"]:
            only_patient += 1
        annotated.append(
            {
                **event,
                "motivo_bloqueio": primary,
                "motivos_bloqueio": "+".join(reasons),
            }
        )
    return {
        "por_categoria": dict(counts),
        "desbloqueaveis_apos_duplicados": only_patient,
        "total": len(blocked_events),
        "_eventos": annotated,
    }
