"""Importa o stock de urgência a partir da ficha validada pela enfermeira."""

from __future__ import annotations

from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.data_migration.paths import data_dir
from apps.pharmacy.constants import OrigemMovimentoStock
from apps.pharmacy.import_plan import build_import_plan
from apps.pharmacy.models import MedicamentoUrgencia
from apps.pharmacy.services.stock_service import StockUrgenciaError, StockUrgenciaService

DEFAULT_FILES = (
    "stock_urgencia_validacao.xlsx",
    "stock_final_validacao_enfermagem.xlsx",
)


def default_source() -> Path:
    base = data_dir() / "private" / "sauvida_atual"
    for name in DEFAULT_FILES:
        path = base / name
        if path.is_file():
            return path
    return base / DEFAULT_FILES[0]


class Command(BaseCommand):
    help = "Importa itens de stock de urgência (dry-run por omissão). Não inventa quantidades."

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true", default=False)
        parser.add_argument("--apply", action="store_true")
        parser.add_argument("--file", type=str, default="")
        parser.add_argument("--actor-email", type=str, default="")

    def handle(self, *args, **options):
        apply = bool(options["apply"]) and not options["dry_run"]
        path = Path(options["file"]) if options["file"] else default_source()
        if not path.is_file():
            raise CommandError(f"Ficheiro não encontrado: {path}")
        plan = build_import_plan(path)
        actor = None
        email = (options["actor_email"] or "").strip()
        if email:
            from django.contrib.auth import get_user_model

            User = get_user_model()
            actor = User.objects.filter(email__iexact=email).first()
            if not actor:
                raise CommandError(f"Utilizador não encontrado: {email}")
        if apply and not actor:
            raise CommandError("--actor-email é obrigatório para --apply.")
        if apply and plan["a_criar"] == 0 and plan["a_actualizar"] == 0:
            raise CommandError("Nenhum item VALIDO para importar. Preencha a ficha da enfermeira.")

        created = updated = 0
        if apply:
            try:
                with transaction.atomic():
                    for item in plan["a_criar_itens"]:
                        obs = item["observacoes"]
                        if item["nome_foto"] and item["nome_foto"] != item["nome"]:
                            extra = f"Nome da foto: {item['nome_foto']}"
                            obs = f"{obs} | {extra}".strip(" |")
                        StockUrgenciaService.criar_item(
                            nome=item["nome"],
                            categoria=item["tipo"],
                            unidade=item["unidade"],
                            quantidade_inicial=item["quantidade"] or 0,
                            stock_minimo=item["stock_minimo"],
                            validade=item["validade"],
                            observacoes=obs,
                            quantidade_texto_original=item.get("quantidade_texto_original") or "",
                            operador=actor,
                            origem=OrigemMovimentoStock.STOCK_INICIAL_CLINICA,
                        )
                        created += 1
                    for item in plan["a_actualizar_itens"]:
                        obj = MedicamentoUrgencia.objects.get(nome__iexact=item["nome"])
                        obj.unidade = item["unidade"]
                        obj.stock_minimo = item["stock_minimo"]
                        if item["validade"]:
                            obj.validade = item["validade"]
                        obj.save()
                        if (item["quantidade"] or 0) > 0 and obj.quantidade_stock == 0:
                            StockUrgenciaService.registar_movimento(
                                obj,
                                tipo="ENTRADA",
                                quantidade=item["quantidade"],
                                motivo="Stock inicial da clínica",
                                operador=actor,
                                origem=OrigemMovimentoStock.STOCK_INICIAL_CLINICA,
                            )
                        updated += 1
            except StockUrgenciaError as exc:
                raise CommandError(str(exc)) from exc
        else:
            created = plan["a_criar"]
            updated = plan["a_actualizar"]

        self.stdout.write(f"ficheiro: {path}")
        self.stdout.write(f"apply: {apply}")
        self.stdout.write(f"encontrados: {plan['encontrados']}")
        self.stdout.write(f"validos: {plan['validos']}")
        self.stdout.write(f"a_criar: {created}")
        self.stdout.write(f"a_actualizar: {updated}")
        self.stdout.write(f"ignorados: {plan['ignorados']}")
        self.stdout.write(f"pendentes: {plan['pendentes']}")
        self.stdout.write(f"quantidades_iniciais: {plan['quantidades_iniciais']}")
        self.stdout.write(f"por_status: {plan['por_status']}")
        self.stdout.write(f"escrita_bd: {apply}")
        if not apply:
            self.stdout.write(self.style.WARNING("Dry-run — nenhuma escrita na BD."))
        else:
            self.stdout.write(self.style.SUCCESS("Importação aplicada."))
