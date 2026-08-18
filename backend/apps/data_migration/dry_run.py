"""Dry-run contra a BD SGCS — sem escrita."""

from __future__ import annotations

import csv
from difflib import SequenceMatcher
from pathlib import Path

from apps.authentication.models import UserRole
from apps.data_migration.constants import FONTE_MIGRACAO, NAME_FUZZY_MIN
from apps.data_migration.phones import normalize_phone
from apps.data_migration.text import fold_for_match

SAFE_MATCH = "CORRESPONDENCIA_SEGURA"
REVIEW_MATCH = "REVISAR"
NEW_PATIENT = "PACIENTE_NOVO"


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def match_patient_to_sgcs(row: dict[str, str], sgcs_patients: list[dict[str, str]]) -> dict[str, str]:
    processo = (row.get("numero_processo_antigo") or "").strip()
    phone = normalize_phone(row.get("telefone") or "")
    name_fold = fold_for_match(row.get("nome_normalizado") or row.get("nome_original") or "")
    dob = (row.get("data_nascimento") or "").strip()

    for existing in sgcs_patients:
        if processo and existing["patient_number"] == processo:
            return {"resultado": SAFE_MATCH, "prioridade": "1", "sgcs_id": existing["id"], "motivo": "Número de processo antigo exacto"}
    for existing in sgcs_patients:
        if phone and existing["phone"] == phone:
            existing_fold = fold_for_match(existing["full_name"])
            ratio = SequenceMatcher(None, name_fold, existing_fold).ratio()
            if ratio >= 0.85:
                return {
                    "resultado": SAFE_MATCH,
                    "prioridade": "2",
                    "sgcs_id": existing["id"],
                    "motivo": "Telefone exacto + nome compatível",
                }
            return {
                "resultado": REVIEW_MATCH,
                "prioridade": "2",
                "sgcs_id": existing["id"],
                "motivo": "Telefone exacto mas nome pouco compatível",
            }
    for existing in sgcs_patients:
        if dob and existing["birth_date"] == dob and fold_for_match(existing["full_name"]) == name_fold:
            return {
                "resultado": SAFE_MATCH,
                "prioridade": "3",
                "sgcs_id": existing["id"],
                "motivo": "Nome exacto + data de nascimento",
            }
    for existing in sgcs_patients:
        if fold_for_match(existing["full_name"]) == name_fold:
            return {
                "resultado": REVIEW_MATCH,
                "prioridade": "4",
                "sgcs_id": existing["id"],
                "motivo": "Nome exacto sem outros identificadores — não fundir automaticamente",
            }
    best_id, best_score = "", 0.0
    for existing in sgcs_patients:
        ratio = SequenceMatcher(None, name_fold, fold_for_match(existing["full_name"])).ratio()
        if ratio > best_score:
            best_score = ratio
            best_id = existing["id"]
    if best_score >= NAME_FUZZY_MIN:
        return {
            "resultado": REVIEW_MATCH,
            "prioridade": "5",
            "sgcs_id": best_id,
            "motivo": "Nome semelhante — não fundir automaticamente",
        }
    return {"resultado": NEW_PATIENT, "prioridade": "", "sgcs_id": "", "motivo": "Sem correspondência SGCS"}


def load_sgcs_patients() -> list[dict[str, str]]:
    from apps.patients.models import Patient

    rows: list[dict[str, str]] = []
    for patient in Patient.objects.filter(is_deleted=False).iterator():
        rows.append(
            {
                "id": str(patient.pk),
                "patient_number": patient.patient_number,
                "full_name": patient.full_name,
                "phone": normalize_phone(patient.phone),
                "birth_date": patient.birth_date.isoformat() if patient.birth_date else "",
            }
        )
    return rows


def load_sgcs_doctors() -> list[dict[str, str]]:
    from django.contrib.auth import get_user_model

    User = get_user_model()
    doctors = []
    for user in User.objects.filter(role=UserRole.MEDICO, is_active=True):
        doctors.append({"id": str(user.pk), "full_name": user.get_full_name(), "email": user.email})
    return doctors


def map_doctors_exact(staging_doctors: list[dict[str, str]], sgcs_doctors: list[dict[str, str]]) -> list[dict[str, str]]:
    index = {fold_for_match(doc["full_name"]): doc for doc in sgcs_doctors}
    mapped = []
    for row in staging_doctors:
        folded = fold_for_match(row.get("nome_normalizado") or "")
        updated = dict(row)
        if not folded:
            updated["estado_mapeamento"] = "REVISAR"
            updated["observacoes"] = "Nome de médico insuficiente. Não criar utilizador."
            mapped.append(updated)
            continue
        match = index.get(folded)
        if match:
            updated["utilizador_sgcs"] = match["email"]
            updated["estado_mapeamento"] = "MATCH_CONFIRMADO"
            updated["observacoes"] = "Correspondência exacta de nome com utilizador MEDICO existente."
            mapped.append(updated)
            continue
        best, best_score = None, 0.0
        for doc in sgcs_doctors:
            score = SequenceMatcher(None, folded, fold_for_match(doc["full_name"])).ratio()
            if score > best_score:
                best, best_score = doc, score
        if best and best_score >= NAME_FUZZY_MIN:
            updated["utilizador_sgcs"] = ""
            updated["estado_mapeamento"] = "POSSIVEL_MATCH"
            updated["observacoes"] = "Nome semelhante a um MEDICO existente — não associar automaticamente."
        else:
            updated["utilizador_sgcs"] = ""
            updated["estado_mapeamento"] = "SEM_CORRESPONDENCIA"
            updated["observacoes"] = "Sem correspondência. Não criar utilizador médico automaticamente."
        mapped.append(updated)
    return mapped


def run_dry_run(staging_dir: Path) -> dict:
    patients = read_csv(staging_dir / "pacientes_migracao_sauvida.csv")
    historico = read_csv(staging_dir / "historico_clinico_sauvida.csv")
    financeiro = read_csv(staging_dir / "historico_financeiro_sauvida.csv")
    stock = read_csv(staging_dir / "stock_referencia_sauvida.csv")
    review = read_csv(staging_dir / "migracao_revisao_manual.csv")
    duplicates = read_csv(staging_dir / "duplicados_pacientes.csv")
    doctors = read_csv(staging_dir / "medicos_historicos.csv")
    exames = read_csv(staging_dir / "mapeamento_exames_historicos.csv")

    sgcs_patients = load_sgcs_patients()
    sgcs_doctors = load_sgcs_doctors()
    mapped_doctors = map_doctors_exact(doctors, sgcs_doctors)

    results = [match_patient_to_sgcs(row, sgcs_patients) for row in patients]
    safe = sum(1 for item in results if item["resultado"] == SAFE_MATCH)
    review_matches = sum(1 for item in results if item["resultado"] == REVIEW_MATCH)
    novos = sum(1 for item in results if item["resultado"] == NEW_PATIENT)

    events: dict[str, int] = {}
    for row in historico:
        events[row.get("tipo_evento") or "OUTRO"] = events.get(row.get("tipo_evento") or "OUTRO", 0) + 1

    lab_events = [row for row in historico if row.get("tipo_evento") == "LABORATORIO"]
    lab_event_states: dict[str, int] = {}
    for row in lab_events:
        state = row.get("estado_mapeamento") or "REVISAR"
        lab_event_states[state] = lab_event_states.get(state, 0) + 1
    lab_desc_states: dict[str, int] = {}
    for row in exames:
        state = row.get("estado") or "REVISAR"
        lab_desc_states[state] = lab_desc_states.get(state, 0) + 1

    ignored = sum(1 for row in review if row.get("tipo") in {"LINHA_SEM_PACIENTE", "DESCRICAO_INSUFICIENTE", "ERRO_EXCEL"})

    from apps.data_migration.staging import write_csv

    write_csv(
        staging_dir / "medicos_historicos.csv",
        ["nome_original", "nome_normalizado", "utilizador_sgcs", "estado_mapeamento", "observacoes"],
        mapped_doctors,
    )

    return {
        "fonte": FONTE_MIGRACAO,
        "linhas_analisadas": len(historico) + len(stock),
        "pacientes_candidatos": len(patients),
        "pacientes_novos": novos,
        "correspondencias_seguras": safe,
        "possiveis_duplicados_sgcs": review_matches,
        "pares_duplicados_internos": len(duplicates),
        "registos_incompletos": sum(1 for row in patients if row.get("estado_migracao") == "DADOS_INSUFICIENTES"),
        "eventos_historicos": len(historico),
        "consultas": events.get("CONSULTA", 0),
        "controlos": events.get("CONTROLO", 0),
        "laboratorio": events.get("LABORATORIO", 0),
        "ecografias": events.get("ECOGRAFIA", 0),
        "cirurgias": events.get("CIRURGIA", 0),
        "laboratorio_mapeado_alinhado": lab_event_states.get("ALINHADO", 0),
        "laboratorio_mapeado_possivel": lab_event_states.get("POSSIVEL", 0),
        "laboratorio_mapeado_ambiguo": lab_event_states.get("AMBIGUO", 0),
        "laboratorio_sem_correspondencia": lab_event_states.get("SEM_CORRESPONDENCIA", 0),
        "lab_descricoes_unicas": len(exames),
        "lab_desc_alinhado": lab_desc_states.get("ALINHADO", 0),
        "lab_desc_possivel": lab_desc_states.get("POSSIVEL", 0),
        "lab_desc_ambiguo": lab_desc_states.get("AMBIGUO", 0),
        "lab_desc_sem_correspondencia": lab_desc_states.get("SEM_CORRESPONDENCIA", 0),
        "registos_financeiros": len(financeiro),
        "medicamentos_materiais": len(stock),
        "registos_revisao": len(review),
        "registos_ignorados": ignored,
        "medicos_historicos": len(doctors),
        "medicos_match_confirmado": sum(1 for row in mapped_doctors if row.get("estado_mapeamento") == "MATCH_CONFIRMADO"),
        "medicos_possivel_match": sum(1 for row in mapped_doctors if row.get("estado_mapeamento") == "POSSIVEL_MATCH"),
        "medicos_sem_correspondencia": sum(1 for row in mapped_doctors if row.get("estado_mapeamento") == "SEM_CORRESPONDENCIA"),
        "medicos_revisar": sum(1 for row in mapped_doctors if row.get("estado_mapeamento") == "REVISAR"),
        "medicos_mapeados": sum(1 for row in mapped_doctors if row.get("estado_mapeamento") == "MATCH_CONFIRMADO"),
        "escrita_bd": False,
        "apply": False,
    }
