"""Auditoria agregada do Excel histórico."""

from __future__ import annotations

from pathlib import Path

from apps.data_migration.excel import HistoricalWorkbook
from apps.data_migration.staging import build_staging, default_output_dir, project_root_from


def audit_excel(path: Path, output_dir: Path | None = None) -> dict:
    root = project_root_from()
    destination = output_dir or default_output_dir(root)
    stats = build_staging(path, destination, root)
    with HistoricalWorkbook(path) as workbook:
        audit = workbook.audit()
    stats["folhas"] = len(audit.sheets)
    stats["folhas_nomes"] = [sheet.name for sheet in audit.sheets]
    stats["linhas_totais"] = audit.total_rows
    stats["formulas"] = audit.formula_cells
    stats["erros_excel"] = audit.excel_errors
    return stats
