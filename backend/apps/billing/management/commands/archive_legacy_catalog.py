"""Arquiva catálogo provisório (fora da receção operacional)."""

from django.core.management.base import BaseCommand

from apps.billing.constants import CATALOGO_VERSAO_ATIVA, CATALOGO_VERSAO_LEGADO
from apps.billing.models import Servico


class Command(BaseCommand):
    help = "Marca serviços não-V1 como arquivados (histórico)"

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        qs = Servico.objects.exclude(versao_catalogo=CATALOGO_VERSAO_ATIVA)
        count = qs.count()
        if options["dry_run"]:
            self.stdout.write(f"[dry-run] Arquivar {count} serviços (versão != {CATALOGO_VERSAO_ATIVA})")
            return
        updated = qs.update(arquivado=True, versao_catalogo=CATALOGO_VERSAO_LEGADO)
        self.stdout.write(self.style.SUCCESS(f"Arquivados: {updated}"))
