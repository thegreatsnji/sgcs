#!/usr/bin/env python
"""Auditoria read-only do Excel histórico SauVida. Não escreve na BD nem no Excel original."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from apps.data_migration.audit import audit_excel
from apps.data_migration.paths import default_output_dir, docs_dir, project_root_from
from apps.data_migration.reports import write_audit_report


def main() -> int:
    root = project_root_from()
    parser = argparse.ArgumentParser(description="Auditoria agregada do Excel histórico SauVida")
    parser.add_argument("--input", required=True, help="Caminho do Excel original (apenas leitura)")
    parser.add_argument("--output", default=str(default_output_dir(root)))
    parser.add_argument("--report", default=str(docs_dir(root) / "MIGRACAO_HISTORICA_AUDITORIA.md"))
    parser.add_argument("--dry-run", action="store_true", help="Escreve staging numa pasta temporária")
    args = parser.parse_args()

    source = Path(args.input)
    if not source.is_file():
        print("Ficheiro Excel não encontrado. Coloque o original em pasta privada e passe --input.", file=sys.stderr)
        return 2

    if args.dry_run:
        import tempfile

        output = Path(tempfile.mkdtemp(prefix="sauvida-audit-"))
    else:
        output = Path(args.output)

    stats = audit_excel(source, output)
    write_audit_report(Path(args.report), stats)
    public = {
        key: stats[key]
        for key in stats
        if key not in {"input", "output"}
    }
    print(json.dumps(public, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
