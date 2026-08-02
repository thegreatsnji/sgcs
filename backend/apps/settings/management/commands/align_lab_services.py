"""Associa tipos de exame laboratorial a serviços de faturação (correspondência explícita)."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.billing.models import Servico
from apps.settings.models import TipoExameLaboratorio

DATA_ROOT = Path(settings.BASE_DIR) / "data"
DEFAULT_EXAMES = DATA_ROOT / "exames_laboratoriais_sauvida.csv"


@dataclass
class AlignSummary:
    alinhados: int = 0
    ignorados: int = 0
    sem_servico: int = 0
    avisos: list[str] = field(default_factory=list)


class Command(BaseCommand):
    help = "Alinha TipoExameLaboratorio.servico com códigos explícitos (sem correspondência ambígua)"

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true")
        parser.add_argument("--apply", action="store_true")
        parser.add_argument("--exames", type=str, default=str(DEFAULT_EXAMES))
        parser.add_argument(
            "--file",
            type=str,
            default="",
            help="Alias de --exames (ex.: backend/data/exames_laboratoriais_reais.csv)",
        )

    def handle(self, *args, **options):
        dry_run = not options["apply"] or options["dry_run"]
        summary = AlignSummary()

        import csv

        path = Path(options["file"] or options["exames"])
        if not path.is_file():
            self.stdout.write(self.style.WARNING(f"Ficheiro omitido: {path}"))
            return

        rows = list(csv.DictReader(path.open(encoding="utf-8-sig")))

        def run():
            for row in rows:
                codigo_tipo = row["codigo"].strip()
                servico_codigo = (row.get("servico_codigo") or "").strip()
                if not servico_codigo:
                    summary.sem_servico += 1
                    continue
                servico = Servico.objects.filter(codigo=servico_codigo).first()
                if not servico:
                    summary.sem_servico += 1
                    summary.avisos.append(f"{codigo_tipo}: serviço {servico_codigo} ausente")
                    continue
                tipo = TipoExameLaboratorio.objects.filter(codigo=codigo_tipo).first()
                if not tipo:
                    summary.ignorados += 1
                    continue
                if tipo.servico_id == servico.pk:
                    summary.ignorados += 1
                    continue
                if tipo.servico_id and tipo.servico_id != servico.pk:
                    summary.avisos.append(
                        f"{codigo_tipo}: já ligado a outro serviço — não alterado"
                    )
                    summary.ignorados += 1
                    continue
                if not dry_run:
                    tipo.servico = servico
                    tipo.save(update_fields=["servico", "updated_at"])
                summary.alinhados += 1

        if options["apply"] and not dry_run:
            with transaction.atomic():
                run()
        else:
            run()

        mode = "DRY-RUN" if dry_run else "APPLY"
        self.stdout.write(self.style.MIGRATE_HEADING(f"=== align_lab_services ({mode}) ==="))
        self.stdout.write(
            f"Alinhados: {summary.alinhados} | Ignorados: {summary.ignorados} | "
            f"Sem serviço: {summary.sem_servico}"
        )
