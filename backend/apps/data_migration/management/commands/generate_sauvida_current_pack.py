"""Gera o pacote privado de reconciliação fotos vs histórico vs V1. Sem escrita na BD."""

from pathlib import Path

from django.core.management.base import BaseCommand

from apps.data_migration.current_ops import write_current_pack
from apps.data_migration.paths import data_dir


class Command(BaseCommand):
    help = "Gera CSVs/Excel privados da reconciliação operacional actual (gitignored)."

    def add_arguments(self, parser):
        parser.add_argument("--output-dir", type=str, default="")

    def handle(self, *args, **options):
        dest = Path(options["output_dir"]) if options["output_dir"] else None
        stats = write_current_pack(dest)
        self.stdout.write(self.style.SUCCESS("Pacote operacional gerado (gitignored, sem importação):"))
        for key, value in stats.items():
            self.stdout.write(f"  {key}: {value}")
        self.stdout.write(f"Pasta dados: {data_dir() / 'private' / 'sauvida_atual'}")
