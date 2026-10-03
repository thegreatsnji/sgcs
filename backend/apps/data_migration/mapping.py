"""Mapeamentos sugeridos — nunca substituem a descrição original."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
from difflib import SequenceMatcher
from typing import Any

from apps.data_migration.catalog import SauvidaCatalog
from apps.data_migration.constants import (
    AUTO_MAP_MIN_CONFIDENCE,
    CONSULTATION_CANONICAL,
    NON_STOCK_KEYWORDS,
    POSSIBLE_MAP_MIN_CONFIDENCE,
)
from apps.data_migration.text import collapse_spaces, fold_for_match, preserve_nfc


def parse_money(value: Any) -> str:
    if value in (None, ""):
        return ""
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return format(Decimal(str(value)).quantize(Decimal("0.01")), "f")
    text = str(value).strip().replace(" ", "").replace("\u00a0", "")
    text = text.replace("FCFA", "").replace("CFA", "").replace("XOF", "")
    text = text.replace(".", "").replace(",", ".") if text.count(",") == 1 and text.count(".") > 1 else text.replace(",", ".")
    try:
        amount = Decimal(text)
    except InvalidOperation:
        return ""
    return format(amount.quantize(Decimal("0.01")), "f")


def money_inconsistent(preco: str, desconto: str, liquido: str) -> bool:
    if not preco or not liquido:
        return False
    try:
        price = Decimal(preco)
        discount = Decimal(desconto or "0")
        net = Decimal(liquido)
    except InvalidOperation:
        return True
    return abs((price - discount) - net) > Decimal("1.00")


def map_consultation(description: str) -> dict[str, str]:
    original = collapse_spaces(str(description or ""))
    folded = fold_for_match(original)
    best = ("", "", 0.0, "SEM_CORRESPONDENCIA")
    for needle, canonical, codigo in CONSULTATION_CANONICAL:
        ratio = SequenceMatcher(None, folded, fold_for_match(needle)).ratio()
        if needle in folded:
            ratio = max(ratio, 0.95)
        if ratio > best[2]:
            estado = "ALINHADO" if ratio >= AUTO_MAP_MIN_CONFIDENCE else (
                "POSSIVEL" if ratio >= POSSIBLE_MAP_MIN_CONFIDENCE else "SEM_CORRESPONDENCIA"
            )
            best = (canonical, codigo if estado == "ALINHADO" else "", ratio, estado)
    return {
        "descricao_original": original,
        "descricao_normalizada": preserve_nfc(original),
        "categoria_canonica": best[0],
        "servico_codigo_sgcs": best[1],
        "confianca": f"{best[2]:.2f}" if best[2] else "",
        "estado": best[3] if original else "REVISAR",
    }


EXAM_LOOKUP_ALIASES = {
    "glicemia": "glicose",
    "glicémia": "glicose",
}


def map_exam(description: str, catalog: SauvidaCatalog) -> dict[str, str]:
    original = collapse_spaces(str(description or ""))
    normalized = preserve_nfc(original)
    if not original:
        return {
            "descricao_excel": original,
            "descricao_normalizada": normalized,
            "servico_codigo_sgcs": "",
            "exame_codigo_sgcs": "",
            "confianca": "",
            "estado": "REVISAR",
            "observacoes": "Descrição vazia",
        }
    lookup = EXAM_LOOKUP_ALIASES.get(fold_for_match(original), original)
    ranked = catalog.find_exam(lookup)
    if not ranked:
        return {
            "descricao_excel": original,
            "descricao_normalizada": normalized,
            "servico_codigo_sgcs": "",
            "exame_codigo_sgcs": "",
            "confianca": "0.00",
            "estado": "SEM_CORRESPONDENCIA",
            "observacoes": "",
        }
    item, score = ranked[0]
    second = ranked[1][1] if len(ranked) > 1 else 0.0
    alias_used = fold_for_match(lookup) != fold_for_match(original)
    if alias_used:
        estado = "POSSIVEL"
        servico, exame = "", ""
        observacoes = f"Sinónimo histórico; sugestão: {item.codigo} ({item.nome})"
    elif score >= AUTO_MAP_MIN_CONFIDENCE and (score - second) >= 0.03:
        estado = "ALINHADO"
        servico = item.codigo if item.codigo.startswith("LAB-") else ""
        exame = item.codigo if item.codigo.startswith("EX-") else ""
        if item.codigo.startswith("EX-"):
            servico = item.codigo.replace("EX-", "", 1) if item.codigo.startswith("EX-LAB") else servico
        if item.codigo.startswith("LAB-"):
            exame = f"EX-{item.codigo}" if not exame else exame
        observacoes = ""
    elif score >= POSSIBLE_MAP_MIN_CONFIDENCE:
        estado = "AMBIGUO" if second >= POSSIBLE_MAP_MIN_CONFIDENCE else "POSSIVEL"
        servico, exame = "", ""
        observacoes = f"Sugestão: {item.codigo} ({item.nome})"
    else:
        estado = "SEM_CORRESPONDENCIA"
        servico, exame = "", ""
        observacoes = f"Melhor candidato fraco: {item.codigo}"
    return {
        "descricao_excel": original,
        "descricao_normalizada": normalized,
        "servico_codigo_sgcs": servico,
        "exame_codigo_sgcs": exame,
        "confianca": f"{score:.2f}",
        "estado": estado,
        "observacoes": observacoes,
    }


def map_service_generic(description: str, catalog: SauvidaCatalog, expected_category: str = "") -> dict[str, str]:
    original = collapse_spaces(str(description or ""))
    ranked = catalog.find_service(original)
    if expected_category:
        ranked = [pair for pair in ranked if pair[0].categoria.upper() == expected_category.upper()] or ranked
    if not original:
        return {"servico_codigo_sgcs": "", "estado_mapeamento": "REVISAR", "confianca": ""}
    if not ranked:
        return {"servico_codigo_sgcs": "", "estado_mapeamento": "SEM_CORRESPONDENCIA", "confianca": "0.00"}
    item, score = ranked[0]
    if score >= AUTO_MAP_MIN_CONFIDENCE:
        return {
            "servico_codigo_sgcs": item.codigo,
            "estado_mapeamento": "ALINHADO",
            "confianca": f"{score:.2f}",
        }
    if score >= POSSIBLE_MAP_MIN_CONFIDENCE:
        return {
            "servico_codigo_sgcs": "",
            "estado_mapeamento": "POSSIVEL",
            "confianca": f"{score:.2f}",
            "observacoes": f"Sugestão: {item.codigo}",
        }
    return {
        "servico_codigo_sgcs": "",
        "estado_mapeamento": "SEM_CORRESPONDENCIA",
        "confianca": f"{score:.2f}",
    }


def classify_stock_item(name: str, sheet_type: str) -> str:
    folded = fold_for_match(name)
    if any(keyword in folded for keyword in NON_STOCK_KEYWORDS):
        if "cama" in folded:
            return "OUTRO"
        return "PROCEDIMENTO"
    if sheet_type == "STOCK_MATERIAL":
        return "MATERIAL_CLINICO"
    if sheet_type == "STOCK_MEDICAMENTO":
        return "MEDICAMENTO"
    return "OUTRO"


def suggest_medication_groups(names: list[str]) -> list[dict[str, str]]:
    unique = sorted({preserve_nfc(n) for n in names if collapse_spaces(n)}, key=fold_for_match)
    assigned: dict[str, str] = {}
    group_id = 0
    rows: list[dict[str, str]] = []
    for name in unique:
        folded = fold_for_match(name)
        match_group = ""
        match_score = 0.0
        match_canon = ""
        for other, gid in assigned.items():
            score = SequenceMatcher(None, folded, fold_for_match(other)).ratio()
            if score >= 0.78 and score > match_score:
                match_group = gid
                match_score = score
                match_canon = other
        if not match_group:
            group_id += 1
            match_group = f"MED-{group_id:03d}"
            match_score = 1.0
            match_canon = name
        assigned[name] = match_group
        rows.append(
            {
                "grupo": match_group,
                "nome_original": name,
                "possivel_nome": match_canon,
                "confianca": f"{match_score:.2f}",
                "confirmado": "",
                "observacoes": "A clínica decide o nome canónico. Sem correcção automática.",
            }
        )
    return rows
