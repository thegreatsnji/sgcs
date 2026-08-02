"""Valida backend/data/precos_validacao_clinica.csv sem alterar o original."""

from __future__ import annotations

from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from apps.billing.services.preco_validation_service import (
    export_revisao_csv,
    relatorio_markdown,
    validar_ficheiro_precos,
)

DATA_ROOT = Path(settings.BASE_DIR) / "data"
DOCS_ROOT = Path(settings.BASE_DIR).parent / "docs"


class Command(BaseCommand):
    help = "Valida o ficheiro de preços confirmados pela clínica (Sprint 18)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            type=str,
            default=str(DATA_ROOT / "precos_validacao_clinica.csv"),
        )
        parser.add_argument(
            "--report",
            type=str,
            default=str(DOCS_ROOT / "SPRINT18_VALIDACAO_PRECOS.md"),
        )
        parser.add_argument(
            "--revisao",
            type=str,
            default=str(DATA_ROOT / "precos_validacao_clinica_revisao.csv"),
        )
        parser.add_argument(
            "--fail-on-block",
            action="store_true",
            help="Termina com erro se houver linhas que bloqueiam importação",
        )

    def handle(self, *args, **options):
        path = Path(options["file"])
        if not path.is_file():
            raise CommandError(f"Ficheiro não encontrado: {path}")

        rel = validar_ficheiro_precos(path)
        report_path = Path(options["report"])
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(
            relatorio_markdown(rel, "Sprint 18 — Validação do ficheiro de preços"),
            encoding="utf-8",
        )

        self.stdout.write(self.style.MIGRATE_HEADING("=== validate_precos_validacao_clinica ==="))
        self.stdout.write(
            f"Total: {rel.total} | Válidas: {rel.validas} | Pendentes: {rel.pendentes} | "
            f"Inválidas: {rel.invalidas} | Duplicadas: {rel.duplicadas}"
        )
        self.stdout.write(f"Relatório: {report_path}")

        if export_revisao_csv(path, rel, Path(options["revisao"])):
            self.stdout.write(self.style.WARNING(f"Ficheiro de revisão: {options['revisao']}"))
        else:
            self.stdout.write("Sem ficheiro de revisão (nenhuma linha inválida/duplicada).")

        if options["fail_on_block"] and rel.bloqueia_importacao:
            raise CommandError("Validação bloqueia importação — corrija o ficheiro ou use revisão.")

        if rel.validas == 0 and rel.pendentes == rel.total:
            self.stdout.write(
                self.style.WARNING(
                    "Todas as linhas estão PENDENTES — importação de preços não deve usar --apply."
                )
            )
