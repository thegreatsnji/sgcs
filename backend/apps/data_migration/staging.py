"""Construção determinística do staging (sem escrita na BD)."""

from __future__ import annotations

import csv
import hashlib
from collections import Counter
from pathlib import Path
from typing import Any

from apps.data_migration.catalog import load_catalog
from apps.data_migration.constants import FONTE_MIGRACAO
from apps.data_migration.dates import parse_date
from apps.data_migration.excel import HistoricalWorkbook, event_type_for_row, event_type_for_sheet
from apps.data_migration.mapping import (
    classify_stock_item,
    map_consultation,
    map_exam,
    map_service_generic,
    money_inconsistent,
    parse_money,
    suggest_medication_groups,
)
from apps.data_migration.paths import default_output_dir, project_root_from
from apps.data_migration.patients import (
    PatientCandidate,
    assign_row_patient_id,
    collect_patients,
    detect_duplicates,
)
from apps.data_migration.text import collapse_spaces, fold_for_match, looks_like_person_name, normalize_person_name, preserve_nfc

CSV_FILES = (
    "pacientes_migracao_sauvida.csv",
    "historico_clinico_sauvida.csv",
    "historico_financeiro_sauvida.csv",
    "stock_referencia_sauvida.csv",
    "migracao_revisao_manual.csv",
    "duplicados_pacientes.csv",
    "mapeamento_consultas.csv",
    "mapeamento_exames_historicos.csv",
    "medicamentos_revisao.csv",
    "medicos_historicos.csv",
)


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def _cell(row_values: dict[str, Any], key: str) -> str:
    value = row_values.get(key)
    if value is None:
        return ""
    return collapse_spaces(str(value))


def build_staging(input_xlsx: Path, output_dir: Path, project_root: Path | None = None) -> dict[str, Any]:
    root = project_root or project_root_from()
    catalog = load_catalog(root)
    output_dir.mkdir(parents=True, exist_ok=True)

    raw_rows: list[dict[str, Any]] = []
    review: list[dict[str, str]] = []
    with HistoricalWorkbook(input_xlsx) as workbook:
        audit = workbook.audit()
        source_hash = hashlib.sha256(input_xlsx.read_bytes()).hexdigest()[:16]
        for excel_row in workbook.iter_clinical_rows():
            values = excel_row.values
            date_original, date_iso, date_marker = parse_date(values.get("data"))
            dob_original, dob_iso, dob_marker = parse_date(values.get("data_nascimento"))
            preco = parse_money(values.get("preco"))
            desconto = parse_money(values.get("desconto"))
            liquido = parse_money(values.get("valor_liquido"))
            nome = _cell(values, "nome")
            descricao = _cell(values, "descricao")
            record = {
                "folha": excel_row.sheet,
                "sheet_type": excel_row.sheet_type,
                "linha": excel_row.row_number,
                "nome": nome,
                "telefone": values.get("telefone"),
                "residencia": _cell(values, "residencia"),
                "data_nascimento": dob_original,
                "data_nascimento_iso": dob_iso,
                "idade": _cell(values, "idade"),
                "sexo": _cell(values, "sexo"),
                "processo": _cell(values, "processo"),
                "data_original": date_original,
                "data_iso": date_iso,
                "data_marker": date_marker or dob_marker,
                "medico": _cell(values, "medico"),
                "tipo_operacao": _cell(values, "tipo_operacao"),
                "descricao": descricao,
                "preco": preco,
                "desconto": desconto,
                "valor_liquido": liquido,
                "formulas": ";".join(excel_row.formulas),
                "excel_errors": ";".join(excel_row.excel_errors),
            }
            raw_rows.append(record)
            _collect_row_reviews(record, review)

    clinical_rows = [row for row in raw_rows if row["sheet_type"] != "RESUMO_FINANCEIRO"]
    patients = collect_patients(clinical_rows)
    duplicates = detect_duplicates(patients)
    assign_row_patient_id(clinical_rows, patients)
    assign_row_patient_id(raw_rows, patients)

    historico, consultas_map, exames_map = _build_history(clinical_rows, catalog, review)
    financeiro = _build_finance(clinical_rows)
    stock, med_review = _build_stock(clinical_rows, review)
    medicos = _build_doctors(clinical_rows)

    patient_rows = [_patient_to_row(patient) for patient in patients]
    _write_outputs(
        output_dir,
        patient_rows,
        historico,
        financeiro,
        stock,
        review,
        duplicates,
        consultas_map,
        exames_map,
        med_review,
        medicos,
    )

    stats = _stats(
        audit,
        patients,
        duplicates,
        historico,
        financeiro,
        stock,
        medicos,
        review,
        consultas_map,
        exames_map,
        med_review,
    )
    stats["fonte"] = FONTE_MIGRACAO
    stats["source_hash"] = source_hash
    stats["input"] = str(input_xlsx)
    stats["output"] = str(output_dir)
    return stats


def _collect_row_reviews(record: dict[str, Any], review: list[dict[str, str]]) -> None:
    linha = str(record["linha"])
    folha = record["folha"]
    if record["excel_errors"]:
        review.append(_issue("ERRO_EXCEL", folha, linha, "", "Erro Excel na linha", record["excel_errors"], "Rever célula na fonte"))
    if record["data_marker"] == "DATA_SUSPEITA":
        review.append(_issue("DATA_SUSPEITA", folha, linha, "", "Data suspeita", record["data_original"], "Não corrigir automaticamente"))
    if record["sheet_type"] not in {"RESUMO_FINANCEIRO", "STOCK_MEDICAMENTO", "STOCK_MATERIAL"} and not looks_like_person_name(record["nome"]):
        review.append(_issue("LINHA_SEM_PACIENTE", folha, linha, "", "Linha sem paciente identificável", "", "Rever manualmente"))
    if record["sheet_type"] not in {"RESUMO_FINANCEIRO"} and not record["descricao"] and not record.get("tipo_operacao") and record["sheet_type"] not in {"STOCK_MEDICAMENTO", "STOCK_MATERIAL"}:
        review.append(_issue("DESCRICAO_INSUFICIENTE", folha, linha, "", "Sem descrição suficiente", "", "Rever manualmente"))
    if money_inconsistent(record["preco"], record["desconto"], record["valor_liquido"]):
        review.append(
            _issue(
                "PRECO_INCONSISTENTE",
                folha,
                linha,
                "",
                "Preço/desconto/líquido inconsistente",
                f"{record['preco']}|{record['desconto']}|{record['valor_liquido']}",
                "Rever valores originais",
            )
        )


def _build_history(
    rows: list[dict[str, Any]],
    catalog,
    review: list[dict[str, str]],
) -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    historico: list[dict[str, str]] = []
    consultas: dict[str, dict[str, str]] = {}
    exames: dict[str, dict[str, str]] = {}
    index = 0
    for row in rows:
        if row["sheet_type"] in {"STOCK_MEDICAMENTO", "STOCK_MATERIAL"}:
            continue
        if not row["descricao"] and not row.get("tipo_operacao") and not looks_like_person_name(row["nome"]):
            continue
        index += 1
        event_type = event_type_for_row(
            row["sheet_type"],
            row.get("tipo_operacao") or "",
            row.get("descricao") or "",
        )
        descricao = row["descricao"] or row.get("tipo_operacao") or ""
        mapped_service = map_service_generic(
            descricao,
            catalog,
            expected_category={
                "ECOGRAFIA": "ECOGRAFIA",
                "CIRURGIA": "CIRURGIA",
                "LABORATORIO": "LABORATORIO",
                "CONSULTA": "CONSULTA",
                "CONTROLO": "CONSULTA",
            }.get(row["sheet_type"], ""),
        )
        if event_type == "CONSULTA":
            mapped = map_consultation(descricao)
            consultas[fold_for_match(descricao)] = mapped
            if mapped["estado"] in {"POSSIVEL", "AMBIGUO", "REVISAR", "SEM_CORRESPONDENCIA"}:
                review.append(
                    _issue(
                        "CONSULTA_AMBIGUA",
                        row["folha"],
                        str(row["linha"]),
                        row.get("migration_patient_id", ""),
                        "Consulta com mapeamento incerto",
                        descricao,
                        mapped.get("categoria_canonica", ""),
                    )
                )
            servico_codigo = mapped["servico_codigo_sgcs"] or mapped_service.get("servico_codigo_sgcs", "")
            estado = mapped["estado"]
            descricao_norm = mapped["descricao_normalizada"]
        elif event_type == "LABORATORIO":
            mapped = map_exam(descricao, catalog)
            exames[fold_for_match(descricao)] = mapped
            if mapped["estado"] != "ALINHADO":
                review.append(
                    _issue(
                        "EXAME_AMBIGUO",
                        row["folha"],
                        str(row["linha"]),
                        row.get("migration_patient_id", ""),
                        "Exame sem correspondência automática",
                        descricao,
                        mapped.get("observacoes", ""),
                    )
                )
            servico_codigo = mapped["servico_codigo_sgcs"]
            estado = mapped["estado"]
            descricao_norm = mapped["descricao_normalizada"]
        else:
            servico_codigo = mapped_service.get("servico_codigo_sgcs", "")
            estado = mapped_service.get("estado_mapeamento", "SEM_CORRESPONDENCIA")
            descricao_norm = preserve_nfc(descricao)
            if event_type in {"ECOGRAFIA", "CIRURGIA"} and estado != "ALINHADO":
                review.append(
                    _issue(
                        f"{event_type}_REVISAR",
                        row["folha"],
                        str(row["linha"]),
                        row.get("migration_patient_id", ""),
                        "Evento estruturado só com dados da fonte; mapeamento SGCS incerto",
                        descricao,
                        mapped_service.get("observacoes", ""),
                    )
                )
        historico.append(
            {
                "historico_id": f"MIG-H-{index:05d}",
                "migration_patient_id": row.get("migration_patient_id", ""),
                "data_evento": row["data_iso"],
                "data_original": row["data_original"],
                "tipo_evento": event_type if event_type != "OUTRO" or descricao else "OUTRO",
                "descricao_original": descricao,
                "descricao_normalizada": descricao_norm,
                "medico_original": row["medico"],
                "medico_mapeado": "",
                "servico_original": descricao,
                "servico_codigo_sgcs": servico_codigo,
                "preco_original": row["preco"],
                "desconto_original": row["desconto"],
                "valor_liquido_original": row["valor_liquido"],
                "folha_origem": row["folha"],
                "linha_origem": row["linha"],
                "fonte": FONTE_MIGRACAO,
                "estado_mapeamento": estado,
                "revisar": "SIM" if estado != "ALINHADO" or not row.get("migration_patient_id") else "",
                "observacoes": "Sem nota operatória/resultado clínico — apenas o que a fonte contém.",
            }
        )
    return historico, list(consultas.values()), list(exames.values())


def _build_finance(rows: list[dict[str, Any]]) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for row in rows:
        if not (row["preco"] or row["valor_liquido"]):
            continue
        out.append(
            {
                "migration_patient_id": row.get("migration_patient_id", ""),
                "data": row["data_iso"],
                "tipo_servico": event_type_for_row(
                    row["sheet_type"],
                    row.get("tipo_operacao") or "",
                    row.get("descricao") or "",
                ),
                "descricao": row["descricao"],
                "preco": row["preco"],
                "desconto": row["desconto"],
                "valor_liquido": row["valor_liquido"],
                "medico": row["medico"],
                "folha_origem": row["folha"],
                "linha_origem": row["linha"],
                "fonte": FONTE_MIGRACAO,
                "revisar": "SIM" if money_inconsistent(row["preco"], row["desconto"], row["valor_liquido"]) else "",
            }
        )
    return out


def _build_stock(
    rows: list[dict[str, Any]], review: list[dict[str, str]]
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    items: dict[str, dict[str, Any]] = {}
    med_names: list[str] = []
    for row in rows:
        if row["sheet_type"] not in {"STOCK_MEDICAMENTO", "STOCK_MATERIAL"}:
            continue
        name = row["descricao"] or row["nome"]
        if not name:
            continue
        original, normalized = name, preserve_nfc(name)
        key = fold_for_match(normalized)
        tipo = classify_stock_item(normalized, row["sheet_type"])
        if tipo == "PROCEDIMENTO" or tipo == "OUTRO":
            review.append(
                _issue(
                    "ITEM_NAO_STOCK",
                    row["folha"],
                    str(row["linha"]),
                    row.get("migration_patient_id", ""),
                    "Item excluído do stock inicial automático",
                    original,
                    tipo,
                )
            )
        current = items.get(key)
        if current is None:
            items[key] = {
                "nome_original": original,
                "nome_normalizado": normalized,
                "tipo": tipo,
                "unidade": "",
                "preco_observado": row["preco"] or row["valor_liquido"],
                "numero_ocorrencias": 1,
                "primeira_ocorrencia": row["data_iso"],
                "ultima_ocorrencia": row["data_iso"],
                "possivel_nome_canonico": "",
                "confirmado_clinica": "",
                "quantidade_inicial": "",
                "observacoes": "Quantidade inicial vazia — a enfermeira confirma o stock físico actual.",
            }
        else:
            current["numero_ocorrencias"] += 1
            if row["data_iso"]:
                if not current["primeira_ocorrencia"] or row["data_iso"] < current["primeira_ocorrencia"]:
                    current["primeira_ocorrencia"] = row["data_iso"]
                if not current["ultima_ocorrencia"] or row["data_iso"] > current["ultima_ocorrencia"]:
                    current["ultima_ocorrencia"] = row["data_iso"]
        if tipo == "MEDICAMENTO":
            med_names.append(original)
            review.append(
                _issue(
                    "MEDICAMENTO_AMBIGUO",
                    row["folha"],
                    str(row["linha"]),
                    "",
                    "Grafia de medicamento para revisão da clínica",
                    original,
                    "Não corrigir automaticamente",
                )
            )
    stock = sorted(items.values(), key=lambda item: fold_for_match(item["nome_normalizado"]))
    for item in stock:
        item["numero_ocorrencias"] = str(item["numero_ocorrencias"])
        item["quantidade_inicial"] = ""
    return stock, suggest_medication_groups(med_names)


def _build_doctors(rows: list[dict[str, Any]]) -> list[dict[str, str]]:
    seen: dict[str, dict[str, str]] = {}
    for row in rows:
        original, normalized = normalize_person_name(row["medico"])
        if not looks_like_person_name(normalized or original):
            continue
        key = fold_for_match(normalized)
        seen.setdefault(
            key,
            {
                "nome_original": original,
                "nome_normalizado": normalized,
                "utilizador_sgcs": "",
                "estado_mapeamento": "SEM_CORRESPONDENCIA",
                "observacoes": "Não criar utilizador médico automaticamente.",
            },
        )
    return sorted(seen.values(), key=lambda item: fold_for_match(item["nome_normalizado"]))


def _patient_to_row(patient: PatientCandidate) -> dict[str, str]:
    return {
        "migration_id": patient.migration_id,
        "nome_original": patient.nome_original,
        "nome_normalizado": patient.nome_normalizado,
        "telefone": patient.telefone,
        "residencia": patient.residencia,
        "data_nascimento": patient.data_nascimento,
        "idade_registada": patient.idade_registada,
        "sexo": patient.sexo,
        "numero_processo_antigo": patient.numero_processo_antigo,
        "primeiro_registo": patient.primeiro_registo,
        "ultimo_registo": patient.ultimo_registo,
        "fontes": "|".join(sorted(patient.fontes)),
        "numero_eventos": str(patient.numero_eventos),
        "estado_migracao": patient.estado_migracao,
        "revisar": patient.revisar,
        "observacoes": patient.observacoes,
    }


def _issue(tipo: str, folha: str, linha: str, identificador: str, problema: str, valor: str, sugestao: str) -> dict[str, str]:
    return {
        "tipo": tipo,
        "folha": folha,
        "linha": linha,
        "identificador": identificador,
        "problema": problema,
        "valor_original": valor,
        "sugestao": sugestao,
        "decisao": "",
        "observacoes": "",
    }


def _write_outputs(
    output_dir: Path,
    patients,
    historico,
    financeiro,
    stock,
    review,
    duplicates,
    consultas,
    exames,
    med_review,
    medicos,
) -> None:
    write_csv(
        output_dir / "pacientes_migracao_sauvida.csv",
        [
            "migration_id",
            "nome_original",
            "nome_normalizado",
            "telefone",
            "residencia",
            "data_nascimento",
            "idade_registada",
            "sexo",
            "numero_processo_antigo",
            "primeiro_registo",
            "ultimo_registo",
            "fontes",
            "numero_eventos",
            "estado_migracao",
            "revisar",
            "observacoes",
        ],
        patients,
    )
    write_csv(
        output_dir / "historico_clinico_sauvida.csv",
        [
            "historico_id",
            "migration_patient_id",
            "data_evento",
            "data_original",
            "tipo_evento",
            "descricao_original",
            "descricao_normalizada",
            "medico_original",
            "medico_mapeado",
            "servico_original",
            "servico_codigo_sgcs",
            "preco_original",
            "desconto_original",
            "valor_liquido_original",
            "folha_origem",
            "linha_origem",
            "fonte",
            "estado_mapeamento",
            "revisar",
            "observacoes",
        ],
        historico,
    )
    write_csv(
        output_dir / "historico_financeiro_sauvida.csv",
        [
            "migration_patient_id",
            "data",
            "tipo_servico",
            "descricao",
            "preco",
            "desconto",
            "valor_liquido",
            "medico",
            "folha_origem",
            "linha_origem",
            "fonte",
            "revisar",
        ],
        financeiro,
    )
    write_csv(
        output_dir / "stock_referencia_sauvida.csv",
        [
            "nome_original",
            "nome_normalizado",
            "tipo",
            "unidade",
            "preco_observado",
            "numero_ocorrencias",
            "primeira_ocorrencia",
            "ultima_ocorrencia",
            "possivel_nome_canonico",
            "confirmado_clinica",
            "quantidade_inicial",
            "observacoes",
        ],
        stock,
    )
    write_csv(
        output_dir / "migracao_revisao_manual.csv",
        ["tipo", "folha", "linha", "identificador", "problema", "valor_original", "sugestao", "decisao", "observacoes"],
        review,
    )
    write_csv(
        output_dir / "duplicados_pacientes.csv",
        ["grupo", "paciente_a", "paciente_b", "motivo", "pontuacao", "decisao", "observacoes"],
        duplicates,
    )
    write_csv(
        output_dir / "mapeamento_consultas.csv",
        ["descricao_original", "descricao_normalizada", "categoria_canonica", "servico_codigo_sgcs", "confianca", "estado"],
        consultas,
    )
    write_csv(
        output_dir / "mapeamento_exames_historicos.csv",
        [
            "descricao_excel",
            "descricao_normalizada",
            "servico_codigo_sgcs",
            "exame_codigo_sgcs",
            "confianca",
            "estado",
            "observacoes",
        ],
        exames,
    )
    write_csv(
        output_dir / "medicamentos_revisao.csv",
        ["grupo", "nome_original", "possivel_nome", "confianca", "confirmado", "observacoes"],
        med_review,
    )
    write_csv(
        output_dir / "medicos_historicos.csv",
        ["nome_original", "nome_normalizado", "utilizador_sgcs", "estado_mapeamento", "observacoes"],
        medicos,
    )


def _stats(audit, patients, duplicates, historico, financeiro, stock, medicos, review, consultas, exames, med_review) -> dict[str, Any]:
    events = Counter(row["tipo_evento"] for row in historico)
    dup_c = sum(1 for row in duplicates if row["observacoes"] == "POSSIVEL_DUPLICADO")
    dup_b = sum(1 for row in duplicates if row["observacoes"] == "REVISAR_DUPLICADO")
    dup_exact = sum(1 for row in duplicates if row["observacoes"] == "PROVAVEL_MESMO_PACIENTE")
    lab_desc_states = Counter(row.get("estado") or "REVISAR" for row in exames)
    lab_event_states = Counter(
        row.get("estado_mapeamento") or "REVISAR"
        for row in historico
        if row.get("tipo_evento") == "LABORATORIO"
    )
    isos = sorted(row["data_evento"] for row in historico if row.get("data_evento"))
    years = Counter(iso[:4] for iso in isos)
    dominant_year = int(years.most_common(1)[0][0]) if years else 0
    outside_dominant = 0
    if dominant_year:
        outside_dominant = sum(
            1 for iso in isos if abs(int(iso[:4]) - dominant_year) > 1
        )
    stock_tipos = Counter(item.get("tipo") or "OUTRO" for item in stock)
    return {
        "folhas": len(audit.sheets),
        "folhas_nomes": [sheet.name for sheet in audit.sheets],
        "linhas_totais": audit.total_rows,
        "formulas": audit.formula_cells,
        "erros_excel": audit.excel_errors,
        "pacientes_candidatos": len(patients),
        "nomes_unicos_normalizados": len({p.nome_fold for p in patients}),
        "pacientes_com_telefone": sum(1 for p in patients if p.telefone),
        "pacientes_com_residencia": sum(1 for p in patients if p.residencia),
        "pacientes_incompletos": sum(1 for p in patients if p.estado_migracao == "DADOS_INSUFICIENTES"),
        "pacientes_revisao": sum(1 for p in patients if p.revisar == "SIM"),
        "pacientes_pronto": sum(1 for p in patients if p.estado_migracao == "PRONTO"),
        "duplicados_exactos": dup_exact,
        "duplicados_nivel_b": dup_b,
        "possiveis_duplicados": dup_c,
        "pares_duplicados": len(duplicates),
        "eventos_historicos": len(historico),
        "eventos_com_paciente": sum(1 for row in historico if row.get("migration_patient_id")),
        "eventos_sem_paciente": sum(1 for row in historico if not row.get("migration_patient_id")),
        "consultas": events.get("CONSULTA", 0),
        "controlos": events.get("CONTROLO", 0),
        "laboratorio": events.get("LABORATORIO", 0),
        "ecografias": events.get("ECOGRAFIA", 0),
        "cirurgias": events.get("CIRURGIA", 0),
        "eventos_outro": events.get("OUTRO", 0),
        "registos_financeiros": len(financeiro),
        "stock_descricoes_unicas": len(stock),
        "medicamentos_candidatos": stock_tipos.get("MEDICAMENTO", 0),
        "materiais_candidatos": stock_tipos.get("MATERIAL_CLINICO", 0),
        "procedimentos_em_vendas": stock_tipos.get("PROCEDIMENTO", 0),
        "stock_outro": stock_tipos.get("OUTRO", 0),
        "grupos_medicamentos_revisao": len({item.get("grupo") for item in med_review if item.get("grupo")}),
        "linhas_medicamentos_revisao": len(med_review),
        "medicos": len(medicos),
        "data_minima": isos[0] if isos else "",
        "data_maxima": isos[-1] if isos else "",
        "ano_dominante": dominant_year,
        "datas_fora_periodo_dominante": outside_dominant,
        "datas_malformadas": sum(1 for row in historico if row.get("data_original") and not row.get("data_evento")),
        "datas_suspeitas": sum(1 for row in review if row["tipo"] == "DATA_SUSPEITA"),
        "registos_invalidos": sum(1 for row in review if row["tipo"] in {"ERRO_EXCEL", "LINHA_SEM_PACIENTE", "DESCRICAO_INSUFICIENTE"}),
        "itens_revisao": len(review),
        "consultas_mapeadas": len(consultas),
        "exames_mapeados": len(exames),
        "lab_descricoes_unicas": len(exames),
        "lab_desc_alinhado": lab_desc_states.get("ALINHADO", 0),
        "lab_desc_possivel": lab_desc_states.get("POSSIVEL", 0),
        "lab_desc_ambiguo": lab_desc_states.get("AMBIGUO", 0),
        "lab_desc_sem_correspondencia": lab_desc_states.get("SEM_CORRESPONDENCIA", 0),
        "lab_desc_revisar": lab_desc_states.get("REVISAR", 0),
        "lab_eventos_alinhado": lab_event_states.get("ALINHADO", 0),
        "lab_eventos_possivel": lab_event_states.get("POSSIVEL", 0),
        "lab_eventos_ambiguo": lab_event_states.get("AMBIGUO", 0),
        "lab_eventos_sem_correspondencia": lab_event_states.get("SEM_CORRESPONDENCIA", 0),
        "lab_eventos_revisar": lab_event_states.get("REVISAR", 0),
        "stock_quantidade_inicial_vazia": all(item.get("quantidade_inicial", "") == "" for item in stock),
    }
