"""Rollback por batch_id da migração histórica SauVida."""

from django.core.management.base import BaseCommand, CommandError

from apps.data_migration.rollback import rollback_batch


class Command(BaseCommand):
    help = "Remove apenas objectos criados pela migração do lote indicado."

    def add_arguments(self, parser):
        parser.add_argument("--batch-id", required=True)
        parser.add_argument("--dry-run", action="store_true")
        parser.add_argument("--apply", action="store_true")

    def handle(self, *args, **options):
        if options["apply"] and options["dry_run"]:
            raise CommandError("Indique --apply ou --dry-run, não ambos.")
        do_apply = bool(options["apply"]) and not options["dry_run"]
        stats = rollback_batch(options["batch_id"], apply=do_apply)
        self.stdout.write(self.style.MIGRATE_HEADING("=== rollback_sauvida_history ==="))
        for key, value in stats.items():
            self.stdout.write(f"{key}: {value}")
