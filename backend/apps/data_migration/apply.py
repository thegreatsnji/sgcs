"""Plano e execução da importação histórica SauVida (idempotente, com proveniência)."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from django.db import transaction
from django.utils import timezone
from django.utils.dateparse import parse_date

from apps.audit_logs.models import AuditAction
from apps.audit_logs.services import AuditService
from apps.data_migration.blocked import PATIENT_BLOCK_REASONS, classify_blocked_events, event_block_reasons
from apps.data_migration.constants import (
    CREATED_VIA,
    DATE_REVIEW_ACCEPT,
    DOCTOR_REVIEW_MAP,
    FONTE_MIGRACAO,
    LAB_REVIEW_MAPPED,
    LAB_REVIEW_UNLOCK,
    PATIENT_REVIEW_IMPORT,
    PATIENT_REVIEW_MERGE,
    PATIENT_REVIEW_SKIP,
    RECORD_CLASS_HISTORICO,
    VERIFICATION_BLOCKED_DUP,
    VERIFICATION_IMPORTED,
)
from apps.data_migration.dry_run import SAFE_MATCH, load_sgcs_patients, match_patient_to_sgcs
from apps.data_migration.merge import (
    alias_map_from_pairs,
    canonical_migration_id,
    mark_alias_patient,
    pair_ids,
    record_alias,
    resolve_patient_id,
)
from apps.data_migration.review import read_csv
from apps.data_migration.tables import read_first_existing
from apps.data_migration.text import fold_for_match
from apps.patients.constants import HistoryEventType, PatientGender
from apps.patients.models import Patient, PatientHistory
from apps.patients.services.history_service import PatientHistoryService
from apps.patients.services.number_service import PatientNumberService

EVENT_TYPE_MAP = {
    "CONSULTA": HistoryEventType.CONSULTA,
    "CONTROLO": HistoryEventType.CONSULTA,
    "LABORATORIO": HistoryEventType.EXAME,
    "ECOGRAFIA": HistoryEventType.EXAME,
    "CIRURGIA": HistoryEventType.CIRURGIA,
    "OUTRO": HistoryEventType.OUTRO,
}


def split_person_name(normalized: str) -> tuple[str, str]:
    parts = [part for part in (normalized or "").split(" ") if part]
    if not parts:
        return "", ""
    if len(parts) == 1:
        return parts[0], parts[0]
    return parts[0], " ".join(parts[1:])


def map_gender(value: str) -> str:
    folded = (value or "").strip().upper()
    if folded in {"M", "MASCULINO", "H", "HOMEM"}:
        return PatientGender.MASCULINO
    if folded in {"F", "FEMININO", "MULHER"}:
        return PatientGender.FEMININO
    return ""


def _aware(date_iso: str):
    parsed = parse_date(date_iso) if date_iso else None
    if not parsed:
        return None
    return timezone.make_aware(datetime.combine(parsed, datetime.min.time().replace(hour=12)))


def _decisions(path: Path, key: str, value_key: str = "decisao") -> dict[str, str]:
    return {
        (row.get(key) or "").strip(): (row.get(value_key) or "").strip().upper()
        for row in read_csv(path)
        if (row.get(key) or "").strip()
    }


def _patient_review_status(migration_id: str, pairs: list[dict[str, str]]) -> str:
    statuses: list[str] = []
    for pair in pairs:
        a_id = (pair.get("paciente_a_id") or pair.get("paciente_a") or pair.get("id_a") or "").strip()
        b_id = (pair.get("paciente_b_id") or pair.get("paciente_b") or "").strip()
        if migration_id not in {a_id, b_id}:
            continue
        decision = (pair.get("decisao") or "").strip().upper()
        if decision in PATIENT_REVIEW_SKIP:
            return "SKIP"
        if decision in PATIENT_REVIEW_IMPORT:
            statuses.append("IMPORT")
        elif decision == PATIENT_REVIEW_MERGE:
            left, right = pair_ids(pair)
            statuses.append("IMPORT" if migration_id == canonical_migration_id(left, right) else "SKIP")
        else:
            statuses.append("WAIT")
    if not statuses:
        return "WAIT"
    if "SKIP" in statuses and "IMPORT" not in statuses:
        return "SKIP"
    if statuses and all(item == "IMPORT" for item in statuses):
        return "IMPORT"
    return "WAIT"


def _lab_decisions(staging_dir: Path) -> dict[str, str]:
    rows = read_first_existing(
        [
            staging_dir / "validation_pack" / "laboratorio_historico_validacao.xlsx",
            staging_dir / "laboratorio_validacao_historica.xlsx",
            staging_dir / "laboratorio_validacao_historica.xlsx",
            staging_dir / "laboratorio_validacao_historica.csv",
        ]
    )
    result: dict[str, str] = {}
    for row in rows:
        key = fold_for_match(row.get("descricao_excel") or row.get("descricao_historica") or row.get("descricao_original") or "")
        decision = (row.get("decisao") or "").strip().upper()
        if key and decision:
            result[key] = decision
    return result


def _doctor_decisions(staging_dir: Path) -> dict[str, dict[str, str]]:
    rows = read_first_existing(
        [
            staging_dir / "validation_pack" / "medicos_historicos_validacao.xlsx",
            staging_dir / "medicos_validacao_historica.xlsx",
            staging_dir / "medicos_validacao_historica.xlsx",
            staging_dir / "medicos_historicos.csv",
        ]
    )
    result: dict[str, dict[str, str]] = {}
    for row in rows:
        name = fold_for_match(row.get("nome_historico") or row.get("nome_original") or "")
        if name:
            result[name] = {
                "decisao": (row.get("decisao") or "").strip().upper(),
                "utilizador_sgcs": (row.get("utilizador_sgcs_sugerido") or row.get("utilizador_sgcs") or "").strip(),
            }
    return result


def _overlay_pack_decisions(staging_dir: Path, duplicates: list[dict[str, str]], date_decision: dict[str, dict[str, str]]) -> None:
    xlsx_dups = read_first_existing(
        [
            staging_dir / "validation_pack" / "pacientes_duplicados_validacao.xlsx",
            staging_dir / "duplicados_validacao_sauvida.xlsx",
            staging_dir / "duplicados_validacao_sauvida.xlsx",
            staging_dir / "pacientes_bloqueados_validacao.xlsx",
        ]
    )
    xlsx_by_grupo = {(row.get("identificador") or row.get("grupo") or "").strip(): row for row in xlsx_dups}
    if xlsx_by_grupo:
        for pair in duplicates:
            overlay = xlsx_by_grupo.get((pair.get("grupo") or "").strip())
            if overlay and (overlay.get("decisao") or "").strip():
                pair["decisao"] = overlay["decisao"]
    date_rows = read_first_existing(
        [
            staging_dir / "validation_pack" / "datas_suspeitas_validacao.xlsx",
            staging_dir / "datas_validacao_clinica.csv",
        ]
    )
    for row in date_rows:
        hid = (row.get("migration_event_id") or row.get("historico_id") or "").strip()
        if not hid:
            continue
        current = date_decision.get(hid) or {}
        if (row.get("decisao") or "").strip():
            current["decisao"] = row["decisao"]
        if (row.get("data_confirmada") or "").strip():
            current["data_confirmada"] = row["data_confirmada"]
        date_decision[hid] = current


def build_import_plan(staging_dir: Path, *, skip_blocked: bool = True, reviewed_only: bool = False) -> dict[str, Any]:
    patients = read_csv(staging_dir / "pacientes_migracao_sauvida.csv")
    historico = read_csv(staging_dir / "historico_clinico_sauvida.csv")
    financeiro = read_csv(staging_dir / "historico_financeiro_sauvida.csv")
    duplicates = read_csv(staging_dir / "duplicados_para_validacao_clinica.csv") or read_csv(
        staging_dir / "duplicados_pacientes.csv"
    )
    dates = read_csv(staging_dir / "datas_validacao_clinica.csv")
    orphans = read_csv(staging_dir / "eventos_sem_paciente.csv")

    dup_decision = _decisions(staging_dir / "duplicados_para_validacao_clinica.csv", "grupo")
    date_decision = {
        (row.get("migration_event_id") or "").strip(): row
        for row in dates
        if (row.get("migration_event_id") or "").strip()
    }
    _overlay_pack_decisions(staging_dir, duplicates, date_decision)

    blocked_patients: set[str] = set()
    for pair in duplicates:
        grupo = (pair.get("grupo") or "").strip()
        decision = (pair.get("decisao") or dup_decision.get(grupo) or "").strip().upper()
        a_id = (pair.get("paciente_a_id") or pair.get("paciente_a") or "").strip()
        b_id = (pair.get("paciente_b_id") or pair.get("paciente_b") or "").strip()
        if decision == "PESSOAS_DIFERENTES":
            continue
        if decision == "MESMA_PESSOA":
            if b_id:
                blocked_patients.add(b_id)
            continue
        blocked_patients.update({pid for pid in (a_id, b_id) if pid})

    sgcs_patients = load_sgcs_patients()
    ready_patients: list[dict[str, str]] = []
    blocked_patient_rows: list[dict[str, str]] = []
    associate_patients: list[dict[str, str]] = []
    for row in patients:
        mid = (row.get("migration_id") or "").strip()
        match = match_patient_to_sgcs(row, sgcs_patients)
        if mid in blocked_patients:
            blocked_patient_rows.append({**row, "motivo_bloqueio": VERIFICATION_BLOCKED_DUP})
            continue
        if match["resultado"] == SAFE_MATCH:
            associate_patients.append({**row, "sgcs_id": match.get("sgcs_id") or ""})
            continue
        ready_patients.append(row)

    blocked_event_ids: set[str] = set()
    for event in historico:
        hid = (event.get("historico_id") or "").strip()
        date_row = date_decision.get(hid)
        if date_row is not None:
            decision = (date_row.get("decisao") or "").strip().upper()
            if decision not in {"ACEITAR", "CONFIRMADA", "OK"}:
                blocked_event_ids.add(hid)
        if (event.get("tipo_evento") == "LABORATORIO") and (event.get("estado_mapeamento") or "") == "AMBIGUO":
            blocked_event_ids.add(hid)
        if (event.get("migration_patient_id") or "") in blocked_patients:
            blocked_event_ids.add(hid)

    ready_events: list[dict[str, str]] = []
    blocked_events: list[dict[str, str]] = []
    skipped_no_patient: list[dict[str, str]] = []
    lab_structured: list[dict[str, str]] = []
    lab_textual: list[dict[str, str]] = []
    for event in historico:
        hid = (event.get("historico_id") or "").strip()
        pid = (event.get("migration_patient_id") or "").strip()
        if not pid:
            skipped_no_patient.append(event)
            continue
        if hid in blocked_event_ids:
            blocked_events.append(event)
            continue
        if not event.get("data_evento") and hid not in date_decision:
            blocked_events.append(event)
            continue
        ready_events.append(event)
        if event.get("tipo_evento") == "LABORATORIO":
            if event.get("estado_mapeamento") == "ALINHADO":
                lab_structured.append(event)
            else:
                lab_textual.append(event)

    clinical_keys = {(ev.get("folha_origem"), ev.get("linha_origem")) for ev in historico}
    finance_ready: list[dict[str, str]] = []
    finance_blocked: list[dict[str, str]] = []
    finance_skipped: list[dict[str, str]] = []
    for row in financeiro:
        pid = (row.get("migration_patient_id") or "").strip()
        key = (row.get("folha_origem"), row.get("linha_origem"))
        if not pid:
            finance_skipped.append(row)
            continue
        if pid in blocked_patients or (row.get("revisar") or "").upper() == "SIM":
            finance_blocked.append(row)
            continue
        if key in clinical_keys:
            continue
        finance_ready.append(row)

    ready_ids = {row.get("migration_id") for row in ready_patients} | {row.get("migration_id") for row in associate_patients}
    ready_events_importable = [ev for ev in ready_events if ev.get("migration_patient_id") in ready_ids]
    finance_importable = [row for row in finance_ready if row.get("migration_patient_id") in ready_ids]
    finance_on_events = sum(
        1
        for ev in ready_events_importable
        if (ev.get("preco_original") or ev.get("valor_liquido_original"))
    )

    classified = classify_blocked_events(
        blocked_events,
        blocked_patients=blocked_patients,
        date_decision=date_decision,
    )

    if reviewed_only:
        lab_decisions = _lab_decisions(staging_dir)
        doctor_decisions = _doctor_decisions(staging_dir)
        aliases = alias_map_from_pairs(duplicates)
        imported_patient_ids = {
            (meta or {}).get("migration_id")
            for meta in Patient.objects.filter(metadata__source=FONTE_MIGRACAO).values_list("metadata", flat=True)
            if (meta or {}).get("migration_id")
        }
        review_ready: list[dict[str, str]] = []
        still_blocked: list[dict[str, str]] = []
        for row in blocked_patient_rows:
            mid = (row.get("migration_id") or "").strip()
            if mid in aliases:
                still_blocked.append(row)
                continue
            status = _patient_review_status(mid, duplicates)
            if status == "IMPORT" and mid not in imported_patient_ids:
                review_ready.append(row)
            else:
                still_blocked.append(row)
        ready_patients = review_ready
        associate_patients = []
        blocked_patient_rows = still_blocked
        ready_ids = {row.get("migration_id") for row in ready_patients} | imported_patient_ids
        unlocked_events: list[dict[str, str]] = []
        still_blocked_events: list[dict[str, str]] = []
        labs_mapeados = 0
        labs_textuais = 0
        datas_corrigidas = 0
        for event in blocked_events:
            hid = (event.get("historico_id") or "").strip()
            if _existing_history(hid):
                still_blocked_events.append(event)
                continue
            reasons = event_block_reasons(
                event, blocked_patients=blocked_patients, date_decision=date_decision
            )
            ok = True
            for reason in reasons:
                if reason in PATIENT_BLOCK_REASONS:
                    pid = resolve_patient_id(event.get("migration_patient_id") or "", aliases)
                    if pid in ready_ids:
                        continue
                    ok = False
                elif reason == "DATA_SUSPEITA":
                    decision = (date_decision.get(hid) or {}).get("decisao") or ""
                    if decision.strip().upper() in DATE_REVIEW_ACCEPT:
                        if decision.strip().upper() == "CORRIGIR_DATA" and (date_decision.get(hid) or {}).get("data_confirmada"):
                            datas_corrigidas += 1
                        continue
                    ok = False
                elif reason == "LAB_AMBIGUO":
                    key = fold_for_match(event.get("descricao_original") or "")
                    lab_dec = lab_decisions.get(key) or ""
                    if lab_dec in LAB_REVIEW_UNLOCK:
                        if lab_dec in LAB_REVIEW_MAPPED:
                            labs_mapeados += 1
                        elif lab_dec == "MANTER_TEXTUAL":
                            labs_textuais += 1
                        continue
                    ok = False
                else:
                    ok = False
            if ok:
                unlocked_events.append(event)
            else:
                still_blocked_events.append(event)
        ready_events_importable = unlocked_events
        blocked_events = still_blocked_events
        finance_importable = []
        finance_on_events = sum(
            1
            for ev in ready_events_importable
            if (ev.get("preco_original") or ev.get("valor_liquido_original"))
        )
        lab_structured = [ev for ev in ready_events_importable if ev.get("tipo_evento") == "LABORATORIO" and ev.get("estado_mapeamento") == "ALINHADO"]
        lab_textual = [ev for ev in ready_events_importable if ev.get("tipo_evento") == "LABORATORIO" and ev.get("estado_mapeamento") != "ALINHADO"]
        merges_confirmados = sum(1 for pair in duplicates if (pair.get("decisao") or "").strip().upper() == PATIENT_REVIEW_MERGE)
        separados = sum(1 for pair in duplicates if (pair.get("decisao") or "").strip().upper() in PATIENT_REVIEW_IMPORT)
        medicos_mapeados = sum(1 for row in doctor_decisions.values() if row.get("decisao") == DOCTOR_REVIEW_MAP and row.get("utilizador_sgcs"))
    else:
        aliases = {}
        labs_mapeados = 0
        labs_textuais = 0
        datas_corrigidas = 0
        merges_confirmados = 0
        separados = 0
        medicos_mapeados = 0
        doctor_decisions = {}
        lab_decisions = {}

    def _count(tipo: str) -> int:
        return sum(1 for ev in ready_events_importable if ev.get("tipo_evento") == tipo)

    return {
        "fonte": FONTE_MIGRACAO,
        "pacientes_prontos": len(ready_patients),
        "pacientes_associar": len(associate_patients),
        "pacientes_bloqueados": len(blocked_patient_rows),
        "eventos_prontos": len(ready_events_importable),
        "eventos_bloqueados": len(blocked_events),
        "eventos_sem_paciente": len(skipped_no_patient) or len(orphans),
        "consultas_prontas": _count("CONSULTA"),
        "controlos_prontos": _count("CONTROLO"),
        "laboratorio_estruturado": sum(1 for ev in lab_structured if ev.get("migration_patient_id") in ready_ids),
        "laboratorio_textual": sum(1 for ev in lab_textual if ev.get("migration_patient_id") in ready_ids),
        "ecografias_prontas": _count("ECOGRAFIA"),
        "cirurgias_prontas": _count("CIRURGIA"),
        "financeiro_historico_pronto": len(finance_importable) + finance_on_events,
        "datas_bloqueadas": sum(1 for hid, row in date_decision.items() if (row.get("decisao") or "").strip().upper() not in DATE_REVIEW_ACCEPT),
        "itens_ignorados": len(skipped_no_patient) + len(finance_skipped),
        "skip_blocked": skip_blocked,
        "reviewed_only": reviewed_only,
        "pacientes_desbloqueados": len(ready_patients) if reviewed_only else 0,
        "merges_confirmados": merges_confirmados,
        "pacientes_mantidos_separados": separados,
        "eventos_desbloqueados": len(ready_events_importable) if reviewed_only else 0,
        "labs_mapeados": labs_mapeados,
        "labs_mantidos_textuais": labs_textuais,
        "datas_corrigidas": datas_corrigidas,
        "medicos_mapeados": medicos_mapeados,
        "registos_ainda_bloqueados": len(blocked_patient_rows) + len(blocked_events),
        "eventos_desbloqueaveis_apos_duplicados": classified["desbloqueaveis_apos_duplicados"],
        "eventos_bloqueados_por_categoria": classified["por_categoria"],
        "_ready_patients": ready_patients,
        "_associate_patients": associate_patients,
        "_blocked_patients": blocked_patient_rows,
        "_ready_events": ready_events_importable,
        "_blocked_events": blocked_events,
        "_finance_ready": finance_importable,
        "_date_decision": date_decision,
        "_alias_map": aliases,
        "_doctor_decisions": doctor_decisions,
        "_lab_decisions": lab_decisions if reviewed_only else {},
        "_duplicates": duplicates,
    }


def _existing_patient(migration_id: str) -> Patient | None:
    return Patient.objects.filter(metadata__migration_id=migration_id, is_deleted=False).first()


def _existing_history(historico_id: str) -> PatientHistory | None:
    return PatientHistory.objects.filter(
        source_module=FONTE_MIGRACAO,
        metadata__historico_id=historico_id,
    ).first()


def _patient_payload(row: dict[str, str], batch_id: str, user) -> dict[str, Any]:
    first_name, last_name = split_person_name(row.get("nome_normalizado") or row.get("nome_original") or "")
    birth = parse_date(row.get("data_nascimento") or "") if row.get("data_nascimento") else None
    phone = (row.get("telefone") or "").strip()
    gender = map_gender(row.get("sexo") or "")
    processo = (row.get("numero_processo_antigo") or "").strip()
    residencia = (row.get("residencia") or "").strip()
    return {
        "first_name": first_name,
        "last_name": last_name,
        "birth_date": birth,
        "gender": gender,
        "phone": phone,
        "document_number": processo,
        "address_city": residencia,
        "created_by": user,
        "updated_by": user,
        "metadata": {
            "source": FONTE_MIGRACAO,
            "created_via": CREATED_VIA,
            "import_batch": batch_id,
            "migration_id": row.get("migration_id") or "",
            "source_sheets": row.get("fontes") or "",
            "dados_verificados": False,
            "verification_state": VERIFICATION_IMPORTED,
            "record_class": RECORD_CLASS_HISTORICO,
        },
    }


def apply_import(
    staging_dir: Path,
    *,
    batch_id: str,
    user,
    patients_only: bool = False,
    history_only: bool = False,
    skip_blocked: bool = True,
    reviewed_only: bool = False,
    request=None,
) -> dict[str, Any]:
    plan = build_import_plan(staging_dir, skip_blocked=skip_blocked, reviewed_only=reviewed_only)
    created_patients = 0
    reused_patients = 0
    associated = 0
    created_events = 0
    reused_events = 0
    created_finance = 0
    patient_map: dict[str, Patient] = {}

    with transaction.atomic():
        if not history_only:
            for row in plan["_ready_patients"]:
                mid = row.get("migration_id") or ""
                existing = _existing_patient(mid)
                if existing:
                    patient_map[mid] = existing
                    reused_patients += 1
                    continue
                payload = _patient_payload(row, batch_id, user)
                if not payload["first_name"]:
                    continue
                patient = Patient.objects.create(
                    patient_number=PatientNumberService.generate_next(),
                    **payload,
                )
                PatientHistoryService.record(
                    patient,
                    event_type=HistoryEventType.REGISTO,
                    title="Utente importado do registo anterior da clínica",
                    description="Origem histórica SauVida. Dados não verificados na receção.",
                    user=user,
                    source_module=FONTE_MIGRACAO,
                    source_id=patient.pk,
                    metadata={
                        "source": FONTE_MIGRACAO,
                        "import_batch": batch_id,
                        "migration_id": mid,
                        "record_class": RECORD_CLASS_HISTORICO,
                    },
                )
                AuditService.log(
                    action=AuditAction.PATIENT_CREATE,
                    user=user,
                    request=request,
                    description=f"Paciente histórico importado (migration_id={mid}, batch={batch_id}).",
                    resource_type="patient",
                    resource_id=str(patient.pk),
                    metadata={
                        "source": FONTE_MIGRACAO,
                        "import_batch": batch_id,
                        "migration_id": mid,
                        "created_via": CREATED_VIA,
                    },
                )
                patient_map[mid] = patient
                created_patients += 1
            for row in plan["_associate_patients"]:
                mid = row.get("migration_id") or ""
                existing = _existing_patient(mid)
                if existing:
                    patient_map[mid] = existing
                    associated += 1
                    continue
                try:
                    sgcs = Patient.objects.get(pk=int(row.get("sgcs_id") or 0), is_deleted=False)
                except (Patient.DoesNotExist, ValueError, TypeError):
                    continue
                meta = dict(sgcs.metadata or {})
                meta.update(
                    {
                        "source": meta.get("source") or FONTE_MIGRACAO,
                        "import_batch": batch_id,
                        "migration_id": mid,
                        "linked_historical_patient": True,
                    }
                )
                sgcs.metadata = meta
                sgcs.save(update_fields=["metadata", "updated_at"])
                patient_map[mid] = sgcs
                associated += 1

            aliases = plan.get("_alias_map") or {}
            for pair in plan.get("_duplicates") or []:
                if (pair.get("decisao") or "").strip().upper() != PATIENT_REVIEW_MERGE:
                    continue
                left, right = pair_ids(pair)
                canonical_mid = canonical_migration_id(left, right)
                alias_mid = right if left == canonical_mid else left
                canonical = patient_map.get(canonical_mid) or _existing_patient(canonical_mid)
                if not canonical or not alias_mid:
                    continue
                record_alias(
                    canonical,
                    alias_migration_id_value=alias_mid,
                    grupo=(pair.get("grupo") or pair.get("identificador") or ""),
                    actor=user,
                    batch_id=batch_id,
                )
                patient_map[alias_mid] = canonical
                alias_existing = _existing_patient(alias_mid)
                if alias_existing and alias_existing.pk != canonical.pk:
                    mark_alias_patient(
                        alias_existing,
                        canonical_migration_id_value=canonical_mid,
                        actor=user,
                        batch_id=batch_id,
                    )

        if not patients_only:
            if history_only:
                for row in read_csv(staging_dir / "pacientes_migracao_sauvida.csv"):
                    mid = row.get("migration_id") or ""
                    existing = _existing_patient(mid)
                    if existing:
                        patient_map[mid] = existing
                for row in plan["_associate_patients"]:
                    mid = row.get("migration_id") or ""
                    if mid not in patient_map:
                        try:
                            patient_map[mid] = Patient.objects.get(pk=int(row.get("sgcs_id") or 0))
                        except (Patient.DoesNotExist, ValueError, TypeError):
                            continue
            for alias_mid, canonical_mid in (plan.get("_alias_map") or {}).items():
                canonical = patient_map.get(canonical_mid) or _existing_patient(canonical_mid)
                if canonical:
                    patient_map[alias_mid] = canonical

            now = timezone.now()
            doctor_decisions = plan.get("_doctor_decisions") or {}
            lab_decisions = plan.get("_lab_decisions") or {}
            aliases = plan.get("_alias_map") or {}
            for event in plan["_ready_events"]:
                hid = event.get("historico_id") or ""
                if _existing_history(hid):
                    reused_events += 1
                    continue
                orig_pid = event.get("migration_patient_id") or ""
                resolved_pid = resolve_patient_id(orig_pid, aliases)
                patient = patient_map.get(resolved_pid) or patient_map.get(orig_pid)
                if not patient:
                    continue
                date_row = plan["_date_decision"].get(hid) or {}
                date_iso = (date_row.get("data_confirmada") or event.get("data_evento") or "").strip()
                event_date = _aware(date_iso) or now
                tipo = event.get("tipo_evento") or "OUTRO"
                mapping_status = event.get("estado_mapeamento") or ""
                title = (event.get("descricao_original") or tipo).strip()[:200] or tipo
                doc = doctor_decisions.get(fold_for_match(event.get("medico_original") or "")) or {}
                medico_sgcs = doc.get("utilizador_sgcs") if doc.get("decisao") == DOCTOR_REVIEW_MAP else None
                lab_dec = lab_decisions.get(fold_for_match(event.get("descricao_original") or "")) or ""
                if tipo == "LABORATORIO" and lab_dec == "MANTER_TEXTUAL":
                    lab_mode = "TEXTUAL"
                elif tipo == "LABORATORIO" and (mapping_status == "ALINHADO" or lab_dec in LAB_REVIEW_MAPPED):
                    lab_mode = "ESTRUTURADO"
                elif tipo == "LABORATORIO":
                    lab_mode = "TEXTUAL"
                else:
                    lab_mode = ""
                PatientHistoryService.record(
                    patient,
                    event_type=EVENT_TYPE_MAP.get(tipo, HistoryEventType.OUTRO),
                    title=title,
                    description=event.get("descricao_original") or "",
                    user=user,
                    source_module=FONTE_MIGRACAO,
                    event_date=event_date,
                    metadata={
                        "source": FONTE_MIGRACAO,
                        "import_batch": batch_id,
                        "historico_id": hid,
                        "migration_id": resolved_pid,
                        "original_migration_id": orig_pid,
                        "source_sheet": event.get("folha_origem") or "",
                        "source_row": event.get("linha_origem") or "",
                        "imported_at": now.isoformat(),
                        "imported_by": getattr(user, "email", "") or "",
                        "tipo_evento_fonte": tipo,
                        "medico_original": event.get("medico_original") or "",
                        "medico_sgcs": medico_sgcs,
                        "preco_original": event.get("preco_original") or "",
                        "desconto_original": event.get("desconto_original") or "",
                        "valor_liquido_original": event.get("valor_liquido_original") or "",
                        "mapping_status": mapping_status,
                        "mapped_exam_id": event.get("servico_codigo_sgcs") or "",
                        "original_description": event.get("descricao_original") or "",
                        "record_class": RECORD_CLASS_HISTORICO,
                        "lab_mode": lab_mode,
                    },
                )
                created_events += 1

            for row in plan["_finance_ready"]:
                fid = f"FIN-{row.get('folha_origem')}-{row.get('linha_origem')}"
                if PatientHistory.objects.filter(source_module=FONTE_MIGRACAO, metadata__historico_id=fid).exists():
                    continue
                patient = patient_map.get(row.get("migration_patient_id") or "")
                if not patient:
                    continue
                event_date = _aware(row.get("data") or "") or now
                PatientHistoryService.record(
                    patient,
                    event_type=HistoryEventType.OUTRO,
                    title="Registo financeiro histórico",
                    description=row.get("descricao") or "",
                    user=user,
                    source_module=FONTE_MIGRACAO,
                    event_date=event_date,
                    metadata={
                        "source": FONTE_MIGRACAO,
                        "import_batch": batch_id,
                        "historico_id": fid,
                        "source_sheet": row.get("folha_origem") or "",
                        "source_row": row.get("linha_origem") or "",
                        "imported_at": now.isoformat(),
                        "imported_by": getattr(user, "email", "") or "",
                        "medico_original": row.get("medico") or "",
                        "medico_sgcs": None,
                        "preco_original": row.get("preco") or "",
                        "desconto_original": row.get("desconto") or "",
                        "valor_liquido_original": row.get("valor_liquido") or "",
                        "record_class": RECORD_CLASS_HISTORICO,
                        "kind": "REGISTO_FINANCEIRO_HISTORICO",
                    },
                )
                created_finance += 1

    result = {k: v for k, v in plan.items() if not k.startswith("_")}
    result.update(
        {
            "escrita_bd": True,
            "apply": True,
            "import_batch": batch_id,
            "pacientes_criados": created_patients,
            "pacientes_reutilizados": reused_patients,
            "pacientes_associados": associated,
            "eventos_criados": created_events,
            "eventos_reutilizados": reused_events,
            "financeiro_criado": created_finance,
        }
    )
    return result
