"""Auditoria agregada de um lote histórico (sem escrita, sem PII)."""

from __future__ import annotations

import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from apps.data_migration.batch_audit import audit_batch
from apps.data_migration.paths import docs_dir, project_root_from


class Command(BaseCommand):
    help = "Auditoria agregada de um batch histórico SauVida. Não escreve na BD."

    def add_arguments(self, parser):
        parser.add_argument("--batch-id", default="SAUVIDA-HIST-V1")
        parser.add_argument("--json", action="store_true")
        parser.add_argument("--report-path", type=str, default="")

    def handle(self, *args, **options):
        stats = audit_batch(options["batch_id"])
        if options["json"]:
            self.stdout.write(json.dumps(stats, ensure_ascii=False, indent=2, default=str))
        else:
            self.stdout.write(self.style.MIGRATE_HEADING("=== audit_sauvida_history_batch ==="))
            for key in (
                "import_batch",
                "pacientes",
                "historicos",
                "historicos_registo_importacao",
                "historicos_clinicos",
                "historicos_financeiros_extra",
                "audit_logs_associados",
                "orfos",
                "migration_ids_duplicados",
                "provenance_incompleta_pacientes",
                "provenance_incompleta_historico",
                "historicos_em_pacientes_externos",
            ):
                self.stdout.write(f"{key}: {stats.get(key)}")
            self.stdout.write(f"financial_leakage: {stats.get('financial_leakage')}")
            self.stdout.write(f"stock_leakage: {stats.get('stock_leakage')}")
            self.stdout.write(f"tabelas_inesperadas: {stats.get('tabelas_inesperadas')}")
            self.stdout.write(f"por_tipo_clinico: {stats.get('por_tipo_clinico')}")

        report_path = options["report_path"]
        if report_path:
            path = Path(report_path)
        else:
            path = docs_dir(project_root_from()) / "SPRINT21_FASE4_BATCH_AUDIT.md"
        _write_markdown(path, stats)
        if not options["json"]:
            self.stdout.write(f"Relatório: {path}")


def _write_markdown(path: Path, stats: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = [
        ("Patient (batch)", stats.get("pacientes", 0)),
        ("PatientHistory total do lote", stats.get("historicos", 0)),
        ("PatientHistory REGISTO (auxiliares de importação)", stats.get("historicos_registo_importacao", 0)),
        ("PatientHistory clínicos", stats.get("historicos_clinicos", 0)),
        ("PatientHistory financeiro extra", stats.get("historicos_financeiros_extra", 0)),
        ("AuditLog com import_batch", stats.get("audit_logs_associados", 0)),
        ("Eventos órfãos", stats.get("orfos", 0)),
        ("migration_id duplicados", stats.get("migration_ids_duplicados", 0)),
        ("Provenance incompleta (pacientes)", stats.get("provenance_incompleta_pacientes", 0)),
        ("Provenance incompleta (histórico)", stats.get("provenance_incompleta_historico", 0)),
        ("Históricos em pacientes externos", stats.get("historicos_em_pacientes_externos", 0)),
    ]
    for tipo, qty in (stats.get("por_tipo_clinico") or {}).items():
        rows.append((f"Evento clínico {tipo}", qty))
    lines = [
        "# Auditoria do batch histórico",
        "",
        f"**Lote:** `{stats.get('import_batch')}`  ",
        f"**Fonte:** `{stats.get('fonte')}`  ",
        "Apenas agregados. Sem dados identificáveis.",
        "",
        "| Modelo / tipo | Quantidade |",
        "| ------------- | ---------: |",
    ]
    for label, qty in rows:
        lines.append(f"| {label} | {qty} |")
    leak = stats.get("financial_leakage") or {}
    stock = stats.get("stock_leakage") or {}
    lines += [
        "",
        "## Leakage",
        "",
        f"- Financeiro: `{leak}`",
        f"- Stock: `{stock}`",
        f"- Tabelas inesperadas: `{stats.get('tabelas_inesperadas')}`",
        "",
        "AuditLog não é removido pelo rollback (trilha forense). PatientHistory REGISTO é auxiliar de proveniência e conta no rollback.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")
    if not stats.get("import_batch"):
        raise CommandError("Batch vazio.")
