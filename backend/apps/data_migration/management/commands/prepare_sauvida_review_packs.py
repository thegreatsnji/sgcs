"""Gera fichas Excel privadas de validação clínica (gitignored)."""

from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from apps.data_migration.paths import default_output_dir, project_root_from
from apps.data_migration.review_packs import write_validation_pack


class Command(BaseCommand):
    help = "Escreve Excel de revisão na pasta privada de staging. Não escreve na BD."

    def add_arguments(self, parser):
        parser.add_argument("--staging-dir", type=str, default="")

    def handle(self, *args, **options):
        staging = Path(options["staging_dir"] or default_output_dir(project_root_from()))
        if not staging.is_dir():
            raise CommandError(f"Staging não encontrado: {staging}")
        written = write_validation_pack(staging)
        self.stdout.write(self.style.SUCCESS("Pacote de validação gerado em validation_pack/ (gitignored):"))
        for key, path in written.items():
            self.stdout.write(f"  {key}: {path}")
