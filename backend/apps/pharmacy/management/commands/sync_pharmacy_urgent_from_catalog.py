"""Sincroniza medicamentos de urgência a partir do catálogo (categoria MED_URGENCIA)."""

from django.core.management.base import BaseCommand

from apps.billing.models import Servico
from apps.pharmacy.models import MedicamentoUrgencia


class Command(BaseCommand):
    help = "Cria/atualiza registos de stock para serviços MED_URGENCIA do catálogo"

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        dry = options["dry_run"]
        servicos = Servico.objects.filter(categoria="MED_URGENCIA", activo=True).order_by("codigo")
        created = updated = 0
        for s in servicos:
            defaults = {
                "nome": s.nome,
                "servico": s,
                "activo": True,
            }
            if dry:
                exists = MedicamentoUrgencia.objects.filter(codigo=s.codigo).exists()
                self.stdout.write(f"{'exists' if exists else 'create'} {s.codigo}")
                continue
            obj, was_created = MedicamentoUrgencia.objects.update_or_create(
                codigo=s.codigo,
                defaults=defaults,
            )
            if was_created:
                created += 1
            else:
                updated += 1
        if not dry:
            self.stdout.write(self.style.SUCCESS(f"Criados: {created} | Actualizados: {updated}"))
