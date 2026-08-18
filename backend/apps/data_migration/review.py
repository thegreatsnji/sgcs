"""Reclassificação da revisão histórica: bloqueante vs. não bloqueante."""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path
from typing import Any

from apps.data_migration.constants import (
    PRIORITY_CRITICAL,
    PRIORITY_HIGH,
    PRIORITY_INFO,
    PRIORITY_LOW,
    PRIORITY_MEDIUM,
)
from apps.data_migration.staging import write_csv
from apps.data_migration.text import fold_for_match


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def classify_review_row(
    row: dict[str, str],
    *,
    lab_by_desc: dict[str, str],
    historico_by_line: dict[tuple[str, str], dict[str, str]],
) -> dict[str, str]:
    tipo = (row.get("tipo") or "").strip()
    identificador = (row.get("identificador") or "").strip()
    folha = (row.get("folha") or "").strip()
    linha = (row.get("linha") or "").strip()
    hist = historico_by_line.get((folha, linha), {})
    hist_id = hist.get("historico_id") or identificador
    lab_state = lab_by_desc.get(fold_for_match(hist.get("descricao_original") or row.get("valor_original") or ""))

    if tipo == "DATA_SUSPEITA":
        return _prio(
            tipo,
            "DATAS",
            hist_id or f"{folha}:{linha}",
            True,
            PRIORITY_CRITICAL,
            "Data impossível ou fora do período esperado",
            "Confirmar ou corrigir a data na fonte; sem isto o evento não é importado",
        )
    if tipo == "PRECO_INCONSISTENTE":
        return _prio(
            tipo,
            "FINANCEIRO",
            hist_id or f"{folha}:{linha}",
            True,
            PRIORITY_HIGH,
            "Preço/desconto/líquido inconsistente na linha fonte",
            "Confirmar valores originais antes de importar o registo financeiro",
        )
    if tipo == "EXAME_AMBIGUO":
        state = (hist.get("estado_mapeamento") or lab_state or "").strip()
        if state == "AMBIGUO":
            return _prio(
                tipo,
                "LABORATORIO",
                hist_id,
                True,
                PRIORITY_HIGH,
                "Mapeamento laboratorial ambíguo — não associar ao catálogo V1",
                "Escolher o exame SGCS ou manter como histórico textual",
            )
        if state == "POSSIVEL":
            return _prio(
                tipo,
                "LABORATORIO",
                hist_id,
                False,
                PRIORITY_MEDIUM,
                "Correspondência laboratorial possível — importar como texto até confirmação",
                "Opcional: confirmar ligação ao catálogo V1",
            )
        return _prio(
            tipo,
            "LABORATORIO",
            hist_id,
            False,
            PRIORITY_LOW,
            "Exame histórico sem correspondência moderna — importar descrição original",
            "Nenhuma; pode confirmar mapeamento mais tarde",
        )
    if tipo in {"ECOGRAFIA_REVISAR", "CIRURGIA_REVISAR", "CONSULTA_AMBIGUA"}:
        return _prio(
            tipo,
            "EVENTOS",
            hist_id,
            False,
            PRIORITY_LOW,
            "Descrição antiga sem serviço SGCS alinhado — importar como histórico textual",
            "Nenhuma para a importação; mapeamento canónico é posterior",
        )
    if tipo == "MEDICAMENTO_AMBIGUO":
        return _prio(
            tipo,
            "STOCK",
            identificador or f"{folha}:{linha}",
            True,
            PRIORITY_MEDIUM,
            "Nome de medicamento incerto para criar item canónico de stock",
            "Enfermeira confirma nome canónico em stock_validacao_enfermagem.csv — não bloqueia histórico clínico",
        )
    if tipo == "ITEM_NAO_STOCK":
        return _prio(
            tipo,
            "STOCK",
            identificador or f"{folha}:{linha}",
            False,
            PRIORITY_INFO,
            "Item de vendas que não é stock (procedimento/outro)",
            "Nenhuma; não entra no stock actual",
        )
    if tipo == "LINHA_SEM_PACIENTE":
        return _prio(
            tipo,
            "EVENTOS_SEM_PACIENTE",
            f"{folha}:{linha}",
            False,
            PRIORITY_INFO,
            "Serviço sem identificação de utente — não se cria paciente fictício",
            "Arquivar; importar só se a clínica ligar a um utente real",
        )
    if tipo in {"DESCRICAO_INSUFICIENTE", "ERRO_EXCEL"}:
        return _prio(
            tipo,
            "LINHA_TECNICA",
            f"{folha}:{linha}",
            False,
            PRIORITY_INFO,
            "Linha técnica ou descrição insuficiente — não importar",
            "Nenhuma para a migração automática",
        )
    return _prio(
        tipo or "OUTRO",
        "OUTRO",
        identificador or f"{folha}:{linha}",
        False,
        PRIORITY_INFO,
        "Item de revisão informativo",
        "Nenhuma",
    )


def _prio(
    tipo: str,
    categoria: str,
    identificador: str,
    bloqueante: bool,
    prioridade: str,
    motivo: str,
    decisao: str,
) -> dict[str, str]:
    return {
        "tipo": tipo,
        "categoria": categoria,
        "identificador_migracao": identificador,
        "bloqueante": "SIM" if bloqueante else "NAO",
        "prioridade": prioridade,
        "motivo": motivo,
        "decisao_necessaria": decisao,
        "estado": "PENDENTE",
        "observacoes": "",
    }


def _classify_orphan(event: dict[str, str]) -> str:
    sheet = fold_for_match(event.get("folha_origem") or "")
    desc = fold_for_match(event.get("descricao_original") or "")
    if "soma" in sheet or sheet.startswith("soma") or "total" in desc or desc in {"soma", "geral"}:
        return "TOTAL" if "total" in desc or "soma" in desc or "soma" in sheet else "FINANCEIRO_AGREGADO"
    if "soma" in sheet:
        return "FINANCEIRO_AGREGADO"
    if not (event.get("descricao_original") or "").strip():
        return "LINHA_TECNICA"
    return "SERVICO_SEM_IDENTIFICACAO"


def build_prioritized_outputs(staging_dir: Path) -> dict[str, Any]:
    review = read_csv(staging_dir / "migracao_revisao_manual.csv")
    patients = read_csv(staging_dir / "pacientes_migracao_sauvida.csv")
    duplicates = read_csv(staging_dir / "duplicados_pacientes.csv")
    historico = read_csv(staging_dir / "historico_clinico_sauvida.csv")
    financeiro = read_csv(staging_dir / "historico_financeiro_sauvida.csv")
    exames = read_csv(staging_dir / "mapeamento_exames_historicos.csv")
    stock = read_csv(staging_dir / "stock_referencia_sauvida.csv")
    med_review = read_csv(staging_dir / "medicamentos_revisao.csv")
    doctors = read_csv(staging_dir / "medicos_historicos.csv")

    lab_by_desc = {
        fold_for_match(row.get("descricao_excel") or ""): (row.get("estado") or "").strip()
        for row in exames
        if (row.get("descricao_excel") or "").strip()
    }
    historico_by_line = {
        (row.get("folha_origem") or "", row.get("linha_origem") or ""): row for row in historico
    }
    patients_by_id = {row.get("migration_id"): row for row in patients}

    prioritized: list[dict[str, str]] = []
    for row in review:
        prioritized.append(
            classify_review_row(row, lab_by_desc=lab_by_desc, historico_by_line=historico_by_line)
        )

    blocked_patient_ids: set[str] = set()
    dup_rows: list[dict[str, str]] = []
    events_by_patient: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in historico:
        pid = (event.get("migration_patient_id") or "").strip()
        if pid:
            events_by_patient[pid].append(event)

    for pair in duplicates:
        a_id = (pair.get("paciente_a") or "").strip()
        b_id = (pair.get("paciente_b") or "").strip()
        blocked_patient_ids.update({a_id, b_id})
        left = patients_by_id.get(a_id, {})
        right = patients_by_id.get(b_id, {})
        prioritized.append(
            _prio(
                "DUPLICADO_PACIENTE",
                "PACIENTES",
                pair.get("grupo") or f"{a_id}|{b_id}",
                True,
                PRIORITY_CRITICAL,
                "Possível paciente duplicado — não mesclar automaticamente",
                "MESMA_PESSOA, PESSOAS_DIFERENTES ou INDETERMINADO (INDETERMINADO = dois registos)",
            )
        )
        left_types = sorted({ev.get("tipo_evento") or "" for ev in events_by_patient.get(a_id, []) if ev.get("tipo_evento")})
        right_types = sorted({ev.get("tipo_evento") or "" for ev in events_by_patient.get(b_id, []) if ev.get("tipo_evento")})
        dup_rows.append(
            {
                "grupo": pair.get("grupo") or "",
                "nivel": pair.get("observacoes") or "",
                "motivo": pair.get("motivo") or "",
                "pontuacao": pair.get("pontuacao") or "",
                "paciente_a_id": a_id,
                "paciente_a_nome": left.get("nome_original") or "",
                "paciente_a_telefone": left.get("telefone") or "",
                "paciente_a_primeiro_registo": left.get("primeiro_registo") or "",
                "paciente_a_ultimo_registo": left.get("ultimo_registo") or "",
                "paciente_a_eventos": left.get("numero_eventos") or "",
                "paciente_a_tipos": "|".join(left_types),
                "paciente_b_id": b_id,
                "paciente_b_nome": right.get("nome_original") or "",
                "paciente_b_telefone": right.get("telefone") or "",
                "paciente_b_primeiro_registo": right.get("primeiro_registo") or "",
                "paciente_b_ultimo_registo": right.get("ultimo_registo") or "",
                "paciente_b_eventos": right.get("numero_eventos") or "",
                "paciente_b_tipos": "|".join(right_types),
                "decisao": pair.get("decisao") or "",
                "observacoes": "INDETERMINADO = não mesclar; preferir dois registos a uma fusão incorrecta.",
            }
        )

    for doc in doctors:
        if (doc.get("estado_mapeamento") or "") in {"", "SEM_CORRESPONDENCIA", "POSSIVEL_MATCH", "REVISAR"}:
            prioritized.append(
                _prio(
                    "MEDICO_SEM_MATCH",
                    "MEDICOS",
                    doc.get("nome_normalizado") or "medico",
                    False,
                    PRIORITY_LOW,
                    "Médico histórico sem utilizador MEDICO correspondente — não criar conta",
                    "Opcional: mapear administrativamente mais tarde",
                )
            )

    orphans: list[dict[str, str]] = []
    for event in historico:
        if (event.get("migration_patient_id") or "").strip():
            continue
        classe = _classify_orphan(event)
        orphans.append(
            {
                "historico_id": event.get("historico_id") or "",
                "classificacao": classe,
                "tipo_evento": event.get("tipo_evento") or "",
                "data_original": event.get("data_original") or "",
                "folha_origem": event.get("folha_origem") or "",
                "linha_origem": event.get("linha_origem") or "",
                "descricao_original": event.get("descricao_original") or "",
                "preco_original": event.get("preco_original") or "",
                "importar": "NAO",
                "observacoes": "Sem paciente identificável — não criar utente fictício.",
            }
        )

    dates_rows: list[dict[str, str]] = []
    for event in historico:
        marker_rows = [
            item
            for item in review
            if item.get("tipo") == "DATA_SUSPEITA"
            and item.get("folha") == event.get("folha_origem")
            and item.get("linha") == event.get("linha_origem")
        ]
        if not marker_rows:
            continue
        dates_rows.append(
            {
                "migration_event_id": event.get("historico_id") or "",
                "data_original": event.get("data_original") or "",
                "data_interpretada": event.get("data_evento") or "",
                "folha": event.get("folha_origem") or "",
                "contexto": (event.get("tipo_evento") or "") + " — descrição na fonte privada",
                "decisao": "",
                "data_confirmada": "",
                "observacoes": "Não importar como data válida enquanto a clínica não confirmar.",
            }
        )

    canon_by_fold = {
        fold_for_match(row.get("nome_original") or ""): row.get("possivel_nome") or ""
        for row in med_review
    }
    stock_rows: list[dict[str, str]] = []
    for item in stock:
        last = item.get("ultima_ocorrencia") or ""
        stock_rows.append(
            {
                "nome_original": item.get("nome_original") or "",
                "possivel_nome_canonico": item.get("possivel_nome_canonico")
                or canon_by_fold.get(fold_for_match(item.get("nome_original") or ""), ""),
                "categoria_sugerida": item.get("tipo") or "",
                "ocorrencias_historicas": item.get("numero_ocorrencias") or "",
                "utilizado_recentemente": "SIM" if last.startswith("2026") or last.startswith("2025") else "NAO",
                "manter_no_stock": "",
                "nome_confirmado": "",
                "unidade": item.get("unidade") or "",
                "quantidade_actual": "",
                "stock_minimo": "",
                "validade": "",
                "observacoes": "Não importar quantidade inicial. A enfermeira preenche manter_no_stock e quantidade_actual.",
            }
        )

    write_csv(
        staging_dir / "migracao_revisao_priorizada.csv",
        [
            "tipo",
            "categoria",
            "identificador_migracao",
            "bloqueante",
            "prioridade",
            "motivo",
            "decisao_necessaria",
            "estado",
            "observacoes",
        ],
        prioritized,
    )
    write_csv(
        staging_dir / "duplicados_para_validacao_clinica.csv",
        [
            "grupo",
            "nivel",
            "motivo",
            "pontuacao",
            "paciente_a_id",
            "paciente_a_nome",
            "paciente_a_telefone",
            "paciente_a_primeiro_registo",
            "paciente_a_ultimo_registo",
            "paciente_a_eventos",
            "paciente_a_tipos",
            "paciente_b_id",
            "paciente_b_nome",
            "paciente_b_telefone",
            "paciente_b_primeiro_registo",
            "paciente_b_ultimo_registo",
            "paciente_b_eventos",
            "paciente_b_tipos",
            "decisao",
            "observacoes",
        ],
        dup_rows,
    )
    write_csv(
        staging_dir / "eventos_sem_paciente.csv",
        [
            "historico_id",
            "classificacao",
            "tipo_evento",
            "data_original",
            "folha_origem",
            "linha_origem",
            "descricao_original",
            "preco_original",
            "importar",
            "observacoes",
        ],
        orphans,
    )
    write_csv(
        staging_dir / "datas_validacao_clinica.csv",
        [
            "migration_event_id",
            "data_original",
            "data_interpretada",
            "folha",
            "contexto",
            "decisao",
            "data_confirmada",
            "observacoes",
        ],
        dates_rows,
    )
    write_csv(
        staging_dir / "stock_validacao_enfermagem.csv",
        [
            "nome_original",
            "possivel_nome_canonico",
            "categoria_sugerida",
            "ocorrencias_historicas",
            "utilizado_recentemente",
            "manter_no_stock",
            "nome_confirmado",
            "unidade",
            "quantidade_actual",
            "stock_minimo",
            "validade",
            "observacoes",
        ],
        stock_rows,
    )

    blocking = [row for row in prioritized if row["bloqueante"] == "SIM"]
    stats = {
        "total_revisao": len(prioritized),
        "total_bloqueante": len(blocking),
        "total_nao_bloqueante": len(prioritized) - len(blocking),
        "pacientes_bloqueados": len({pid for pid in blocked_patient_ids if pid}),
        "pares_duplicados": len(dup_rows),
        "eventos_bloqueados_data": len(dates_rows),
        "laboratorio_bloqueado": sum(1 for row in blocking if row["categoria"] == "LABORATORIO"),
        "datas_bloqueadas": sum(1 for row in blocking if row["categoria"] == "DATAS"),
        "stock_bloqueado": sum(1 for row in blocking if row["categoria"] == "STOCK"),
        "eventos_sem_paciente": len(orphans),
        "medicos_nao_mapeados": len(doctors),
        "itens_stock_enfermagem": len(stock_rows),
        "financeiro_linhas": len(financeiro),
    }
    return stats
