"""Importa ou actualiza o catálogo de serviços (faturação) a partir de CSV."""

from __future__ import annotations

import csv
from decimal import Decimal, InvalidOperation
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from apps.billing.clinic_scope import EXCLUDED_SERVICE_CATEGORIES
from apps.billing.constants import SERVICE_CATEGORIES
from apps.billing.models import Servico

VALID_CATEGORIES = {code for code, _ in SERVICE_CATEGORIES}


class Command(BaseCommand):
    help = (
        "Importa serviços para apps.billing.models.Servico. "
        "Colunas: codigo,nome,descricao,categoria,preco,activo"
    )

    def add_arguments(self, parser):
        default_path = (
            Path(settings.BASE_DIR).parent / "data" / "clinic" / "catalogo_servicos_sauvida.csv"
        )
        parser.add_argument(
            "--file",
            type=str,
            default=str(default_path),
            help=f"Caminho do CSV (predefinição: {default_path})",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Valida o ficheiro sem gravar na base de dados",
        )
        parser.add_argument(
            "--deactivate-missing",
            action="store_true",
            help="Desactiva serviços cujo código não aparece no CSV",
        )

    def handle(self, *args, **options):
        path = Path(options["file"])
        if not path.is_file():
            raise CommandError(f"Ficheiro não encontrado: {path}")

        dry_run = options["dry_run"]
        deactivate_missing = options["deactivate_missing"]
        rows = self._read_rows(path)
        codes_in_file: set[str] = set()

        created = updated = skipped = excluded = 0
        for row in rows:
            codigo = row["codigo"].strip()
            if not codigo:
                skipped += 1
                continue
            categoria = row["categoria"].strip().upper()
            if categoria in EXCLUDED_SERVICE_CATEGORIES:
                excluded += 1
                if dry_run:
                    self.stdout.write(
                        self.style.WARNING(
                            f"  [excluído SauVida] {codigo} — categoria {categoria} não aplicável"
                        )
                    )
                continue
            codes_in_file.add(codigo)
            if categoria not in VALID_CATEGORIES:
                raise CommandError(
                    f"Categoria inválida '{categoria}' em {codigo}. "
                    f"Válidas: {', '.join(sorted(VALID_CATEGORIES))}"
                )
            try:
                preco = Decimal(row["preco"].strip().replace(",", "."))
            except (InvalidOperation, AttributeError) as exc:
                raise CommandError(f"Preço inválido em {codigo}: {row.get('preco')}") from exc

            activo = row.get("activo", "1").strip().lower() in ("1", "true", "sim", "yes", "s")
            defaults = {
                "nome": row["nome"].strip(),
                "descricao": row.get("descricao", "").strip(),
                "categoria": categoria,
                "preco": preco,
                "activo": activo,
            }
            if dry_run:
                self.stdout.write(f"  [dry-run] {codigo} — {defaults['nome']} ({preco} FCFA)")
                continue

            _, was_created = Servico.objects.update_or_create(
                codigo=codigo,
                defaults=defaults,
            )
            if was_created:
                created += 1
            else:
                updated += 1

        if deactivate_missing and not dry_run:
            deactivated = (
                Servico.objects.exclude(codigo__in=codes_in_file)
                .filter(activo=True)
                .update(activo=False)
            )
            self.stdout.write(self.style.WARNING(f"Serviços desactivados (ausentes no CSV): {deactivated}"))

        if dry_run:
            self.stdout.write(self.style.SUCCESS(f"Validação OK — {len(codes_in_file)} linhas."))
            return

        self.stdout.write(
            self.style.SUCCESS(
                f"Catálogo importado: {created} criados, {updated} actualizados, "
                f"{skipped} ignorados, {excluded} excluídos (não aplicáveis)."
            )
        )

    def _read_rows(self, path: Path) -> list[dict[str, str]]:
        with path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            required = {"codigo", "nome", "categoria", "preco"}
            if not reader.fieldnames or not required.issubset(set(reader.fieldnames)):
                raise CommandError(
                    f"CSV deve incluir colunas: {', '.join(sorted(required))}. "
                    f"Encontrado: {reader.fieldnames}"
                )
            return list(reader)
