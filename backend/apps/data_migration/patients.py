"""Candidatos a paciente e detecção de duplicados (sem fusão automática)."""

from __future__ import annotations

from dataclasses import dataclass, field
from difflib import SequenceMatcher
from typing import Any

from apps.data_migration.constants import DUPLICATE_DECISIONS, NAME_FUZZY_MIN, NAME_PROBABLE_MIN
from apps.data_migration.dates import dates_similar
from apps.data_migration.phones import normalize_phone, phones_compatible
from apps.data_migration.text import fold_for_match, looks_like_person_name, normalize_person_name


@dataclass
class PatientCandidate:
    migration_id: str
    nome_original: str
    nome_normalizado: str
    nome_fold: str
    telefone: str
    residencia: str
    data_nascimento: str
    idade_registada: str
    sexo: str
    numero_processo_antigo: str
    primeiro_registo: str
    ultimo_registo: str
    fontes: set[str] = field(default_factory=set)
    numero_eventos: int = 0
    estado_migracao: str = "PRONTO"
    revisar: str = ""
    observacoes: str = ""
    row_refs: list[str] = field(default_factory=list)


def _blank(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def identity_key(nome_fold: str, telefone: str, processo: str) -> str:
    if processo:
        return f"proc:{fold_for_match(processo)}"
    if telefone:
        return f"tel:{telefone}|nome:{nome_fold}"
    return f"nome:{nome_fold}"


def collect_patients(rows: list[dict[str, Any]]) -> list[PatientCandidate]:
    buckets: dict[str, PatientCandidate] = {}
    order: list[str] = []
    for row in rows:
        original, normalized = normalize_person_name(_blank(row.get("nome")))
        if not looks_like_person_name(normalized or original):
            continue
        phone = normalize_phone(_blank(row.get("telefone")))
        processo = _blank(row.get("processo"))
        key = identity_key(fold_for_match(normalized), phone, processo)
        candidate = buckets.get(key)
        event_date = _blank(row.get("data_iso"))
        fonte = _blank(row.get("folha"))
        if candidate is None:
            candidate = PatientCandidate(
                migration_id="",
                nome_original=original,
                nome_normalizado=normalized,
                nome_fold=fold_for_match(normalized),
                telefone=phone,
                residencia=_blank(row.get("residencia")),
                data_nascimento=_blank(row.get("data_nascimento_iso")),
                idade_registada=_blank(row.get("idade")),
                sexo=_blank(row.get("sexo")),
                numero_processo_antigo=processo,
                primeiro_registo=event_date,
                ultimo_registo=event_date,
            )
            buckets[key] = candidate
            order.append(key)
        candidate.numero_eventos += 1
        if fonte:
            candidate.fontes.add(fonte)
        candidate.row_refs.append(f"{fonte}:{row.get('linha')}")
        if phone and not candidate.telefone:
            candidate.telefone = phone
        if event_date:
            if not candidate.primeiro_registo or event_date < candidate.primeiro_registo:
                candidate.primeiro_registo = event_date
            if not candidate.ultimo_registo or event_date > candidate.ultimo_registo:
                candidate.ultimo_registo = event_date
        for attr, incoming in (
            ("residencia", _blank(row.get("residencia"))),
            ("data_nascimento", _blank(row.get("data_nascimento_iso"))),
            ("idade_registada", _blank(row.get("idade"))),
            ("sexo", _blank(row.get("sexo"))),
            ("numero_processo_antigo", processo),
        ):
            current = getattr(candidate, attr)
            if incoming and not current:
                setattr(candidate, attr, incoming)

    patients = [buckets[key] for key in order]
    patients.sort(key=lambda item: (item.nome_fold, item.telefone, item.numero_processo_antigo))
    for index, patient in enumerate(patients, start=1):
        patient.migration_id = f"MIG-P-{index:05d}"
        _classify_patient_state(patient)
    return patients


def _classify_patient_state(patient: PatientCandidate) -> None:
    notes: list[str] = []
    if not patient.nome_normalizado:
        patient.estado_migracao = "DADOS_INSUFICIENTES"
        notes.append("Nome insuficiente")
    elif not patient.telefone and not patient.data_nascimento and not patient.numero_processo_antigo:
        patient.estado_migracao = "DADOS_INSUFICIENTES"
        notes.append("Sem telefone, data de nascimento ou processo antigo")
    if patient.sexo and patient.sexo.upper() not in {"M", "F", "MASCULINO", "FEMININO", "H", "MULHER", "HOMEM"}:
        notes.append("Sexo não padronizado — não foi inventado um valor SGCS")
        if patient.estado_migracao == "PRONTO":
            patient.estado_migracao = "REVISAR"
    if notes and patient.estado_migracao == "PRONTO":
        patient.estado_migracao = "REVISAR"
    patient.observacoes = "; ".join(notes)
    patient.revisar = "SIM" if patient.estado_migracao != "PRONTO" else ""


def detect_duplicates(patients: list[PatientCandidate]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    group = 0
    for i, left in enumerate(patients):
        for right in patients[i + 1 :]:
            decision, score, motivo = _pair_decision(left, right)
            if not decision:
                continue
            group += 1
            rows.append(
                {
                    "grupo": f"DUP-{group:04d}",
                    "paciente_a": left.migration_id,
                    "paciente_b": right.migration_id,
                    "motivo": motivo,
                    "pontuacao": f"{score:.2f}",
                    "decisao": "",
                    "observacoes": decision,
                }
            )
            for patient in (left, right):
                if decision == DUPLICATE_DECISIONS["C"]:
                    if patient.estado_migracao == "PRONTO":
                        patient.estado_migracao = "DUPLICADO_POSSIVEL"
                        patient.revisar = "SIM"
                elif decision in {DUPLICATE_DECISIONS["A"], DUPLICATE_DECISIONS["B"]}:
                    if patient.estado_migracao in {"PRONTO", "DUPLICADO_POSSIVEL"}:
                        patient.estado_migracao = "REVISAR"
                        patient.revisar = "SIM"
    return rows


def _pair_decision(left: PatientCandidate, right: PatientCandidate) -> tuple[str, float, str]:
    name_score = SequenceMatcher(None, left.nome_fold, right.nome_fold).ratio()
    same_name = left.nome_fold == right.nome_fold
    phone_match = bool(left.telefone and right.telefone and left.telefone == right.telefone)
    phone_partial = phones_compatible(left.telefone, right.telefone)
    dob_match = bool(
        left.data_nascimento
        and right.data_nascimento
        and (
            left.data_nascimento == right.data_nascimento
            or dates_similar(left.data_nascimento, right.data_nascimento, 1)
        )
    )
    age_match = bool(
        left.idade_registada
        and right.idade_registada
        and left.idade_registada == right.idade_registada
    )

    if same_name and phone_match:
        return DUPLICATE_DECISIONS["A"], 1.0, "Nome normalizado + telefone exacto"
    if same_name and (dob_match or (phone_partial and not phone_match)):
        return DUPLICATE_DECISIONS["B"], 0.9, "Nome igual com data/telefone parcial semelhante"
    if name_score >= NAME_PROBABLE_MIN and (phone_partial or dob_match or age_match):
        return DUPLICATE_DECISIONS["B"], name_score, "Nome quase igual com identificador semelhante"
    if name_score >= NAME_FUZZY_MIN:
        return DUPLICATE_DECISIONS["C"], name_score, "Apenas nome semelhante — não fundir"
    return "", 0.0, ""


def index_by_id(patients: list[PatientCandidate]) -> dict[str, PatientCandidate]:
    return {patient.migration_id: patient for patient in patients}


def assign_row_patient_id(rows: list[dict[str, Any]], patients: list[PatientCandidate]) -> None:
    lookup: dict[str, str] = {}
    for patient in patients:
        lookup[identity_key(patient.nome_fold, patient.telefone, patient.numero_processo_antigo)] = (
            patient.migration_id
        )
        lookup[f"nome:{patient.nome_fold}"] = lookup.get(f"nome:{patient.nome_fold}", patient.migration_id)
    for row in rows:
        original, normalized = normalize_person_name(_blank(row.get("nome")))
        if not looks_like_person_name(normalized or original):
            row["migration_patient_id"] = ""
            continue
        key = identity_key(
            fold_for_match(normalized),
            normalize_phone(_blank(row.get("telefone"))),
            _blank(row.get("processo")),
        )
        row["migration_patient_id"] = lookup.get(key) or lookup.get(f"nome:{fold_for_match(normalized)}", "")
