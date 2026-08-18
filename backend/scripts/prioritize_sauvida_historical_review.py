#!/usr/bin/env python
"""Gera CSVs privados de priorização da revisão histórica. Sem escrita na BD."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from apps.data_migration.paths import default_output_dir, project_root_from
from apps.data_migration.review import build_prioritized_outputs


def main() -> int:
    root = project_root_from()
    parser = argparse.ArgumentParser(description="Priorização da revisão histórica SauVida")
    parser.add_argument("--staging-dir", default=str(default_output_dir(root)))
    args = parser.parse_args()
    staging = Path(args.staging_dir)
    if not staging.is_dir():
        print("Pasta de staging não encontrada.", file=sys.stderr)
        return 2
    stats = build_prioritized_outputs(staging)
    print(json.dumps(stats, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
