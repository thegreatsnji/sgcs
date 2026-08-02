"""Congela Catálogo SauVida V1 a partir do CSV real OCR (sem preços pendentes)."""

from __future__ import annotations

import csv
import hashlib
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RELEASES = DATA / "releases"
CATALOGO_REAL = DATA / "catalogo_servicos_sauvida_real.csv"
EXAMES_REAL = DATA / "exames_laboratoriais_reais.csv"

VERSAO = "SAUVIDA_V1"
DATA_VERSAO = "2026-07-31"
ORIGEM = "OCR_FOTOGRAFIAS_CLINICA"
ESTADO_CONGELADO = "CONGELADO"


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _is_pending_row(row: dict) -> bool:
    estado = (row.get("estado") or "").strip().upper()
    pc = (row.get("preco_confirmado") or "").strip().lower()
    preco = (row.get("preco_fcfa") or "").strip()
    if estado == "REVISAR_COM_CLINICA":
        return True
    if pc in ("false", "0", "nao", "não"):
        return True
    if preco.upper() == "REVISAR_COM_CLINICA" or not preco:
        return True
    return False


def freeze_servicos() -> tuple[Path, int, int]:
    RELEASES.mkdir(parents=True, exist_ok=True)
    out = RELEASES / "catalogo_sauvida_v1.csv"
    base_fields = [
        "codigo",
        "nome",
        "categoria",
        "departamento",
        "especialidade",
        "preco_fcfa",
        "operacional",
        "preco_confirmado",
        "origem",
        "observacoes",
        "fotografia",
        "estado",
        "ativo",
        "exige_pedido_medico",
        "gera_resultado",
    ]
    meta_fields = [
        "versao_catalogo",
        "data_versao",
        "confirmado_por",
        "data_confirmacao",
    ]
    fieldnames = base_fields + meta_fields

    seen: dict[str, dict] = {}
    pending_skipped = 0
    with CATALOGO_REAL.open(encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            codigo = row["codigo"].strip()
            if _is_pending_row(row):
                pending_skipped += 1
                continue
            if codigo in seen:
                # Manter primeira linha confirmada; ignorar duplicado OCR
                continue
            seen[codigo] = row

    rows_out = []
    for codigo in sorted(seen.keys()):
        row = seen[codigo]
        rows_out.append(
            {
                **{k: row.get(k, "") for k in base_fields},
                "preco_confirmado": "TRUE",
                "estado": "CONFIRMADO",
                "versao_catalogo": VERSAO,
                "data_versao": DATA_VERSAO,
                "confirmado_por": "",
                "data_confirmacao": "",
            }
        )

    with out.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows_out)

    return out, len(rows_out), pending_skipped


def freeze_exames() -> tuple[Path, int]:
    out = RELEASES / "exames_laboratoriais_sauvida_v1.csv"
    base_fields = [
        "codigo",
        "nome",
        "categoria_laboratorial",
        "tipo_amostra",
        "servico_codigo",
        "preco_fcfa",
        "estado",
        "origem",
        "fotografia",
    ]
    meta_fields = ["versao_catalogo", "data_versao"]
    fieldnames = base_fields + meta_fields

    rows_out = []
    with EXAMES_REAL.open(encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            estado = (row.get("estado") or "").strip().upper()
            preco = (row.get("preco_fcfa") or "").strip()
            if estado == "REVISAR_COM_CLINICA" or not preco:
                continue
            rows_out.append(
                {
                    **{k: row.get(k, "") for k in base_fields},
                    "estado": "CONFIRMADO",
                    "versao_catalogo": VERSAO,
                    "data_versao": DATA_VERSAO,
                }
            )

    with out.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows_out)

    return out, len(rows_out)


def write_manifest(servicos_path: Path, exames_path: Path, servicos_n: int, exames_n: int) -> Path:
    manifest = RELEASES / "catalogo_sauvida_v1_manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "versao_catalogo": VERSAO,
                "data_versao": DATA_VERSAO,
                "origem": ORIGEM,
                "estado": ESTADO_CONGELADO,
                "servicos": servicos_n,
                "exames": exames_n,
                "checksum_servicos_sha256": _sha256(servicos_path),
                "checksum_exames_sha256": _sha256(exames_path),
                "regra_alteracao": "Não editar ficheiros em releases/; criar SAUVIDA_V1_1 ou SAUVIDA_V2",
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    return manifest


def main() -> None:
    if not CATALOGO_REAL.is_file():
        raise SystemExit(f"Catálogo real ausente: {CATALOGO_REAL}")
    serv_path, n_serv, pending = freeze_servicos()
    ex_path, n_ex = freeze_exames()
    manifest = write_manifest(serv_path, ex_path, n_serv, n_ex)
    print(f"V1 serviços: {n_serv} (pendentes omitidos: {pending})")
    print(f"V1 exames: {n_ex}")
    print(f"Manifest: {manifest}")
    print(f"SHA256 serviços: {_sha256(serv_path)[:16]}…")


if __name__ == "__main__":
    main()
