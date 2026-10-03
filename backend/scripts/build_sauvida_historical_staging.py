#!/usr/bin/env python
"""Gera CSVs de staging a partir do Excel histórico. Não escreve na BD."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from apps.data_migration.paths import default_output_dir, docs_dir, project_root_from
from apps.data_migration.reports import write_audit_report
from apps.data_migration.staging import build_staging


def main() -> int:
    root = project_root_from()
    parser = argparse.ArgumentParser(description="Staging histórico SauVida (read-only no Excel)")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", default=str(default_output_dir(root)))
    parser.add_argument("--dry-run", action="store_true", help="Calcula staging em pasta temporária")
    parser.add_argument("--report", action="store_true", help="Actualiza docs/MIGRACAO_HISTORICA_AUDITORIA.md")
    args = parser.parse_args()

    source = Path(args.input)
    if not source.is_file():
        print("Ficheiro Excel não encontrado.", file=sys.stderr)
        return 2

    if args.dry_run:
        import tempfile

        output = Path(tempfile.mkdtemp(prefix="sauvida-staging-"))
    else:
        output = Path(args.output)

    stats = build_staging(source, output, root)
    if args.report:
        write_audit_report(docs_dir(root) / "MIGRACAO_HISTORICA_AUDITORIA.md", stats)
    print(json.dumps({k: v for k, v in stats.items() if k not in {"input", "output"}}, ensure_ascii=False, indent=2))
    print(f"staging={output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
