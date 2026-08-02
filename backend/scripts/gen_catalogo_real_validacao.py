"""Gera catalogo_real_validacao_clinica.csv a partir do catálogo real e duplicados.json."""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOGO = ROOT / "data" / "catalogo_servicos_sauvida_real.csv"
DUPLICADOS = ROOT / "data" / "catalogo_real_duplicados.json"
OUT = ROOT / "data" / "catalogo_real_validacao_clinica.csv"

FIELDNAMES = [
    "codigo",
    "nome",
    "categoria",
    "departamento",
    "preco_extraido_fcfa",
    "preco_confirmado_fcfa",
    "fonte",
    "tipo_pendencia",
    "decisao_clinica",
    "confirmado_por",
    "data_confirmacao",
    "observacoes",
]

CONFLICT_TIPO = {
    "preco_divergente": "PREÇOS_DIVERGENTES",
    "duplicado": "POSSÍVEL_DUPLICADO",
}


def pendencia_from_row(row: dict) -> str:
    estado = (row.get("estado") or "").strip()
    preco = (row.get("preco_fcfa") or "").strip()
    obs = (row.get("observacoes") or "").lower()
    nome = (row.get("nome") or "").strip()
    if estado == "REVISAR_COM_CLINICA" or preco == "REVISAR_COM_CLINICA":
        if not preco or preco == "REVISAR_COM_CLINICA":
            return "PREÇO_AUSENTE"
        if "conflito" in obs or "vs" in obs:
            return "PREÇOS_DIVERGENTES"
        if "duplicado" in obs or "unificar" in obs:
            return "POSSÍVEL_DUPLICADO"
        if "[linha sem nome]" in nome.lower() or len(nome) < 3:
            return "NOME_INCOMPLETO"
        if "manuscrit" in obs or "confirmar" in obs or "provável" in obs:
            return "CLASSIFICAÇÃO_DUVIDOSA"
        return "PREÇO_ILEGÍVEL"
    return "NÃO_APLICÁVEL"


def main() -> None:
    with CATALOGO.open(encoding="utf-8-sig") as f:
        rows_by_code: dict[str, list[dict]] = {}
        for row in csv.DictReader(f):
            rows_by_code.setdefault(row["codigo"], []).append(row)

    conflict_codes: set[str] = set()
    with DUPLICADOS.open(encoding="utf-8") as f:
        grupos = json.load(f)
    for g in grupos:
        for c in g.get("codigos", []):
            conflict_codes.add(c)

    selected_codes: set[str] = set()
    for code, variants in rows_by_code.items():
        for row in variants:
            if (row.get("estado") or "").strip() == "REVISAR_COM_CLINICA":
                selected_codes.add(code)
                break
    selected_codes |= conflict_codes

    out_rows: list[dict] = []
    for code in sorted(selected_codes):
        variants = rows_by_code.get(code, [])
        if not variants:
            out_rows.append(
                {
                    "codigo": code,
                    "nome": "",
                    "categoria": "",
                    "departamento": "",
                    "preco_extraido_fcfa": "",
                    "preco_confirmado_fcfa": "",
                    "fonte": "OCR_FOTOGRAFIAS_CLINICA",
                    "tipo_pendencia": "NECESSITA_VALIDACAO",
                    "decisao_clinica": "",
                    "confirmado_por": "",
                    "data_confirmacao": "",
                    "observacoes": "Código referenciado em grupo de conflito; linha ausente no CSV principal.",
                }
            )
            continue
        for row in variants:
            preco = (row.get("preco_fcfa") or "").strip()
            if preco == "REVISAR_COM_CLINICA":
                preco_ext = ""
            else:
                preco_ext = preco
            tipo = pendencia_from_row(row)
            if code in conflict_codes and tipo == "NÃO_APLICÁVEL":
                g = next((x for x in grupos if code in x.get("codigos", [])), None)
                if g:
                    tipo = CONFLICT_TIPO.get(g.get("tipo", ""), "NECESSITA_VALIDACAO")
            out_rows.append(
                {
                    "codigo": row["codigo"],
                    "nome": row["nome"],
                    "categoria": row["categoria"],
                    "departamento": row.get("departamento", ""),
                    "preco_extraido_fcfa": preco_ext,
                    "preco_confirmado_fcfa": "",
                    "fonte": row.get("origem", "OCR_FOTOGRAFIAS_CLINICA"),
                    "tipo_pendencia": tipo,
                    "decisao_clinica": "",
                    "confirmado_por": "",
                    "data_confirmacao": "",
                    "observacoes": row.get("observacoes", ""),
                }
            )

    with OUT.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(out_rows)
    print(f"Escrito {len(out_rows)} linhas em {OUT}")


if __name__ == "__main__":
    main()
