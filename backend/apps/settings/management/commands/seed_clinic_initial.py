"""Carrega perfil da clínica, departamentos e (opcionalmente) catálogo de serviços."""

from __future__ import annotations

import json
from pathlib import Path

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError

from apps.settings.models import Departamento, PerfilClinica


class Command(BaseCommand):
    help = "Semeia dados institucionais SauVida a partir de data/clinic/*.json"

    def add_arguments(self, parser):
        root = Path(settings.BASE_DIR).parent / "data" / "clinic"
        parser.add_argument(
            "--data-dir",
            type=str,
            default=str(root),
            help=f"Pasta com perfil_clinica.json e departamentos_sauvida.json (predef.: {root})",
        )
        parser.add_argument(
            "--import-catalog",
            action="store_true",
            help="Executa import_servico_catalog após carregar JSON",
        )
        parser.add_argument(
            "--catalog-file",
            type=str,
            default="",
            help="CSV alternativo para import_servico_catalog",
        )

    def handle(self, *args, **options):
        data_dir = Path(options["data_dir"])
        if not data_dir.is_dir():
            raise CommandError(f"Pasta não encontrada: {data_dir}")

        self._seed_perfil(data_dir / "perfil_clinica.json")
        self._seed_departamentos(data_dir / "departamentos_sauvida.json")

        if options["import_catalog"]:
            kwargs = {}
            if options["catalog_file"]:
                kwargs["file"] = options["catalog_file"]
            call_command("import_servico_catalog", **kwargs)

        self.stdout.write(self.style.SUCCESS("Dados iniciais da clínica aplicados."))

    def _seed_perfil(self, path: Path) -> None:
        if not path.is_file():
            self.stdout.write(self.style.WARNING(f"Omitido (sem ficheiro): {path.name}"))
            return
        payload = json.loads(path.read_text(encoding="utf-8"))
        perfil, created = PerfilClinica.objects.get_or_create(pk=1, defaults=payload)
        if not created:
            for key, value in payload.items():
                if hasattr(perfil, key):
                    setattr(perfil, key, value)
            perfil.save()
        self.stdout.write(f"  ✓ perfil da clínica: {perfil.nome}")

    def _seed_departamentos(self, path: Path) -> None:
        if not path.is_file():
            self.stdout.write(self.style.WARNING(f"Omitido (sem ficheiro): {path.name}"))
            return
        items = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(items, list):
            raise CommandError("departamentos_sauvida.json deve ser uma lista de objectos.")
        for item in items:
            codigo = item["codigo"].strip()
            Departamento.objects.update_or_create(
                codigo=codigo,
                defaults={
                    "nome": item["nome"].strip(),
                    "descricao": item.get("descricao", "").strip(),
                    "activo": item.get("activo", True),
                },
            )
            self.stdout.write(f"  ✓ departamento: {codigo}")
