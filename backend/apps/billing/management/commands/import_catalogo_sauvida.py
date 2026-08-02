"""Importação do catálogo SauVida (serviços, departamentos, especialidades, exames lab)."""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass, field
from decimal import Decimal
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.audit_logs.models import AuditAction
from apps.audit_logs.services import AuditService
from apps.billing.clinic_scope import EXCLUDED_SERVICE_CATEGORIES, EXCLUDED_SERVICE_CODES
from apps.billing.constants import (
    DEFAULT_SERVICE_CURRENCY,
    PRICE_REVIEW_MARKER,
    SERVICE_CATEGORY_IMPORT_ALIASES,
)
from apps.billing.models import Servico
from apps.billing.services.catalog_service import (
    ORIGEM_IMPORTACAO_VALIDADA,
    confirmar_preco_servico,
    parse_preco_fcfa,
    registar_alteracao_preco,
)
from django.contrib.auth import get_user_model
from apps.settings.models import Departamento, EspecialidadeMedica, TipoExameLaboratorio

DATA_ROOT = Path(settings.BASE_DIR) / "data"
DEFAULT_CSV = DATA_ROOT / "catalogo_servicos_sauvida.csv"
DEFAULT_JSON = DATA_ROOT / "catalogo_servicos_sauvida.json"
DEFAULT_ESPECIALIDADES = DATA_ROOT / "especialidades_sauvida.csv"
DEFAULT_EXAMES = DATA_ROOT / "exames_laboratoriais_sauvida.csv"

REQUIRED_COLUMNS = {
    "codigo",
    "nome",
    "categoria",
    "departamento",
    "preco_fcfa",
    "ativo",
}


def _bool(value: str) -> bool:
    return str(value).strip().lower() in ("1", "true", "sim", "yes", "s", "activo", "ativo")


def _normalize_categoria(raw: str) -> str:
    key = raw.strip().upper()
    if key in EXCLUDED_SERVICE_CATEGORIES:
        raise ValueError(f"Categoria não aplicável: {raw}")
    mapped = SERVICE_CATEGORY_IMPORT_ALIASES.get(key) or SERVICE_CATEGORY_IMPORT_ALIASES.get(
        raw.strip()
    )
    if not mapped:
        raise ValueError(f"Categoria inválida: {raw}")
    return mapped


VALIDATION_REQUIRED_COLUMNS = {
    "codigo",
    "preco_confirmado_fcfa",
}


@dataclass
class ImportSummary:
    criados: int = 0
    actualizados: int = 0
    ignorados: int = 0
    pendentes: int = 0
    confirmados: int = 0
    erros: list[str] = field(default_factory=list)
    avisos: list[str] = field(default_factory=list)


class Command(BaseCommand):
    help = "Importa catálogo SauVida (dry-run por defeito; use --apply para gravar)"

    def add_arguments(self, parser):
        parser.add_argument("--file", type=str, default=str(DEFAULT_CSV))
        parser.add_argument("--json", type=str, default=str(DEFAULT_JSON))
        parser.add_argument("--especialidades", type=str, default=str(DEFAULT_ESPECIALIDADES))
        parser.add_argument("--exames", type=str, default=str(DEFAULT_EXAMES))
        parser.add_argument("--dry-run", action="store_true", help="Simula (predefinição se --apply ausente)")
        parser.add_argument("--apply", action="store_true", help="Grava na base de dados")
        parser.add_argument("--update-existing", action="store_true", help="Actualiza serviços existentes")
        parser.add_argument("--skip-invalid", action="store_true", help="Ignora linhas inválidas")
        parser.add_argument(
            "--create-missing-relations",
            action="store_true",
            help="Cria departamentos/especialidades ausentes referenciados no CSV",
        )
        parser.add_argument("--report-path", type=str, default="")
        parser.add_argument(
            "--materialize-without-price",
            action="store_true",
            help="Cria/actualiza serviços mesmo sem preço confirmado (preço=0, pendente)",
        )
        parser.add_argument(
            "--actor-email",
            type=str,
            default="",
            help="E-mail do utilizador responsável (importação de preços confirmados)",
        )

    def handle(self, *args, **options):
        apply = options["apply"]
        dry_run = not apply or options["dry_run"]

        summary = ImportSummary()
        User = get_user_model()
        user = None
        if options.get("actor_email"):
            user = User.objects.filter(email=options["actor_email"]).first()
            if not user and options["apply"]:
                raise CommandError(f"Utilizador não encontrado: {options['actor_email']}")

        path = Path(options["file"])
        if not path.is_file():
            raise CommandError(f"Ficheiro não encontrado: {path}")

        rows = self._read_csv(path)
        validation_mode = self._is_validation_file(rows, path)

        if not validation_mode:
            self._bootstrap_departamentos(DATA_ROOT / "departamentos_sauvida.json", summary)
            self._bootstrap_especialidades(Path(options["especialidades"]), summary)

        dept_map = {d.codigo: d for d in Departamento.objects.all()}
        esp_map = {e.codigo: e for e in EspecialidadeMedica.objects.all()}

        if not validation_mode and options["create_missing_relations"]:
            self._seed_relations(rows, dept_map, esp_map, dry_run, summary, options)

        def process():
            for row in rows:
                if validation_mode:
                    self._process_validation_row(
                        row,
                        summary,
                        dry_run=dry_run,
                        skip_invalid=options["skip_invalid"],
                        user=user,
                    )
                else:
                    self._process_row(
                        row,
                        summary,
                        dept_map,
                        esp_map,
                        dry_run=dry_run,
                        update_existing=options["update_existing"],
                        skip_invalid=options["skip_invalid"],
                        user=user,
                        materialize=options["materialize_without_price"],
                    )

        if apply:
            with transaction.atomic():
                process()
                if not validation_mode:
                    self._import_exames(
                        Path(options["exames"]), dry_run=False, summary=summary, dept_map=dept_map
                    )
        else:
            process()
            if not validation_mode:
                self._import_exames(Path(options["exames"]), dry_run=True, summary=summary, dept_map=dept_map)

        self._print_summary(summary, dry_run)
        if options["report_path"]:
            Path(options["report_path"]).write_text(
                json.dumps(summary.__dict__, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )

    def _read_csv(self, path: Path) -> list[dict[str, str]]:
        with path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if not reader.fieldnames:
                raise CommandError("CSV sem cabeçalho.")
            fields = set(reader.fieldnames)
            if VALIDATION_REQUIRED_COLUMNS.issubset(fields):
                return list(reader)
            if not REQUIRED_COLUMNS.issubset(fields):
                raise CommandError(
                    f"Colunas obrigatórias (catálogo): {sorted(REQUIRED_COLUMNS)} "
                    f"ou (validação): {sorted(VALIDATION_REQUIRED_COLUMNS)}. "
                    f"Encontrado: {reader.fieldnames}"
                )
            return list(reader)

    def _is_validation_file(self, rows: list[dict[str, str]], path: Path) -> bool:
        with path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            return bool(reader.fieldnames and VALIDATION_REQUIRED_COLUMNS.issubset(set(reader.fieldnames)))

    def _process_validation_row(self, row, summary, *, dry_run, skip_invalid, user):
        codigo = row.get("codigo", "").strip()
        if not codigo:
            summary.ignorados += 1
            return
        raw_preco = row.get("preco_confirmado_fcfa", "").strip()
        if not raw_preco:
            summary.pendentes += 1
            return
        try:
            preco, pendente = parse_preco_fcfa(raw_preco)
            if pendente or preco is None:
                summary.pendentes += 1
                return
        except ValueError as exc:
            if skip_invalid:
                summary.erros.append(f"{codigo}: {exc}")
                summary.ignorados += 1
                return
            raise CommandError(f"{codigo}: {exc}") from exc

        servico = Servico.objects.filter(codigo=codigo).first()
        if not servico:
            summary.ignorados += 1
            summary.avisos.append(f"{codigo}: serviço não existe na BD — ignorado")
            return

        if dry_run:
            summary.confirmados += 1
            return

        motivo = row.get("observacoes", "").strip()
        confirmado_por = row.get("confirmado_por", "").strip()
        confirmar_preco_servico(
            servico,
            preco,
            user=user,
            motivo=motivo,
            origem=ORIGEM_IMPORTACAO_VALIDADA,
            confirmado_por_nome=confirmado_por,
        )
        summary.confirmados += 1
        summary.actualizados += 1

    def _seed_relations(self, rows, dept_map, esp_map, dry_run, summary, options):
        codes_dept = {r["departamento"].strip() for r in rows if r.get("departamento", "").strip()}
        codes_esp = {r.get("especialidade", "").strip() for r in rows if r.get("especialidade", "").strip()}
        esp_path = Path(options["especialidades"])
        if esp_path.is_file():
            for row in csv.DictReader(esp_path.open(encoding="utf-8-sig")):
                codes_esp.add(row["codigo"].strip())
                codes_dept.add(row.get("departamento", "").strip())

        for code in sorted(codes_dept):
            if not code or code in dept_map:
                continue
            if dry_run:
                summary.avisos.append(f"[dry-run] criar departamento {code}")
                continue
            dept = Departamento.objects.create(codigo=code, nome=code.replace("-", " "), activo=True)
            dept_map[code] = dept

        for code in sorted(codes_esp):
            if not code or code in esp_map:
                continue
            if dry_run:
                summary.avisos.append(f"[dry-run] criar especialidade {code}")
                continue
            esp = EspecialidadeMedica.objects.create(codigo=code, nome=code.replace("-", " "), activo=True)
            esp_map[code] = esp

    def _process_row(
        self,
        row: dict[str, str],
        summary: ImportSummary,
        dept_map,
        esp_map,
        *,
        dry_run: bool,
        update_existing: bool,
        skip_invalid: bool,
        user,
        materialize: bool = False,
    ):
        codigo = row["codigo"].strip()
        if not codigo:
            summary.ignorados += 1
            return
        if codigo in EXCLUDED_SERVICE_CODES:
            summary.ignorados += 1
            return

        try:
            categoria = _normalize_categoria(row["categoria"])
            versao = (row.get("versao_catalogo") or "").strip()
            dept_code = row["departamento"].strip()
            if dept_code not in dept_map:
                raise ValueError(f"Departamento desconhecido: {dept_code}")
            preco, pendente = parse_preco_fcfa(row.get("preco_fcfa"))
            pc_raw = (row.get("preco_confirmado") or "").strip().lower()
            if pc_raw in ("false", "0", "nao", "não"):
                pendente = True
            elif pc_raw in ("true", "1", "sim") and not pendente:
                pendente = False
            estado_row = (row.get("estado") or "").strip().upper()
            if estado_row == "REVISAR_COM_CLINICA":
                pendente = True

            esp = None
            esp_code = (row.get("especialidade") or "").strip()
            if esp_code:
                if esp_code not in esp_map:
                    raise ValueError(f"Especialidade desconhecida: {esp_code}")
                esp = esp_map[esp_code]

            defaults = {
                "nome": row["nome"].strip(),
                "descricao": row.get("descricao", "").strip(),
                "categoria": categoria,
                "departamento": dept_map[dept_code],
                "especialidade": esp,
                "preco": preco if not pendente else Decimal("0"),
                "moeda": DEFAULT_SERVICE_CURRENCY,
                "activo": _bool(row.get("operacional", row.get("ativo", "1"))),
                "exige_pedido_medico": _bool(row.get("exige_pedido_medico", "0")),
                "exige_pagamento_antecipado": _bool(row.get("exige_pagamento_antecipado", "0")),
                "permite_pagamento_parcial": _bool(row.get("permite_pagamento_parcial", "1")),
                "exige_agendamento": _bool(row.get("exige_agendamento", "0")),
                "gera_resultado": _bool(row.get("gera_resultado", "0")),
                "duracao_minutos": int(row["duracao_minutos"]) if row.get("duracao_minutos", "").strip() else None,
                "observacoes": " ".join(
                    filter(
                        None,
                        [
                            row.get("observacoes", "").strip(),
                            (f"Origem: {row['origem']}" if row.get("origem") else ""),
                            (f"Foto: {row['fotografia']}" if row.get("fotografia") else ""),
                        ],
                    )
                )[:500],
                "preco_confirmado": False if pendente else True,
            }
            versao = (row.get("versao_catalogo") or "").strip()
            if versao:
                defaults["versao_catalogo"] = versao
                defaults["arquivado"] = False

            if pendente:
                summary.pendentes += 1
                if not dry_run and materialize:
                    Servico.objects.update_or_create(codigo=codigo, defaults=defaults)
                    summary.criados += 1
                return

            defaults["preco_confirmado"] = True
            if dry_run:
                summary.criados += 1
                return

            existing = Servico.objects.filter(codigo=codigo).first()
            if existing and not update_existing:
                summary.ignorados += 1
                return
            if existing:
                old_price = existing.preco
                for key, val in defaults.items():
                    setattr(existing, key, val)
                existing.save()
                if old_price != existing.preco and user:
                    registar_alteracao_preco(
                        existing, old_price, existing.preco, user=user, origem="importacao"
                    )
                summary.actualizados += 1
            else:
                Servico.objects.create(codigo=codigo, **defaults)
                summary.criados += 1
                AuditService.log(
                    action=AuditAction.CATALOGO_REAL_IMPORTADO,
                    description=f"Serviço importado: {codigo}",
                    metadata={"codigo": codigo, "origem": "import_catalogo_sauvida", "versao": versao},
                )
        except Exception as exc:
            msg = f"{codigo}: {exc}"
            if skip_invalid:
                summary.erros.append(msg)
                summary.ignorados += 1
            else:
                raise CommandError(msg) from exc

    def _import_exames(self, path: Path, *, dry_run: bool, summary: ImportSummary, dept_map):
        if not path.is_file():
            return
        with path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                codigo = row["codigo"].strip()
                servico_codigo = row.get("servico_codigo", "").strip()
                servico = Servico.objects.filter(codigo=servico_codigo).first() if servico_codigo else None
                if dry_run:
                    continue
                TipoExameLaboratorio.objects.update_or_create(
                    codigo=codigo,
                    defaults={
                        "nome": row["nome"].strip(),
                        "categoria": row.get("categoria", "GERAL").strip(),
                        "unidade": row.get("unidade", "").strip(),
                        "valor_referencia": row.get("valor_referencia", "").strip(),
                        "tempo_medio_horas": int(row.get("tempo_medio_horas") or 24),
                        "activo": _bool(row.get("ativo", "1")),
                        "servico": servico,
                        "tipo_amostra": row.get("tipo_amostra", "").strip(),
                        "recipiente": row.get("recipiente", "").strip(),
                        "instrucoes_colheita": row.get("instrucoes_colheita", "").strip(),
                        "exige_jejum": _bool(row.get("exige_jejum", "0")),
                        "ordem": int(row.get("ordem") or 0),
                    },
                )

    def _print_summary(self, summary: ImportSummary, dry_run: bool):
        mode = "DRY-RUN" if dry_run else "APPLY"
        self.stdout.write(self.style.MIGRATE_HEADING(f"=== import_catalogo_sauvida ({mode}) ==="))
        self.stdout.write(
            f"Criados: {summary.criados} | Actualizados: {summary.actualizados} | "
            f"Confirmados: {summary.confirmados} | Ignorados: {summary.ignorados} | "
            f"Pendentes revisão: {summary.pendentes}"
        )
        for err in summary.erros[:20]:
            self.stdout.write(self.style.ERROR(err))
        for av in summary.avisos[:20]:
            self.stdout.write(self.style.WARNING(av))

    def _bootstrap_departamentos(self, path: Path, summary: ImportSummary):
        if not path.is_file():
            return
        items = json.loads(path.read_text(encoding="utf-8"))
        for item in items:
            code = item["codigo"].strip()
            Departamento.objects.update_or_create(
                codigo=code,
                defaults={
                    "nome": item["nome"].strip(),
                    "descricao": item.get("descricao", "").strip(),
                    "activo": item.get("activo", True),
                    "ordem": item.get("ordem", 0),
                },
            )

    def _bootstrap_especialidades(self, path: Path, summary: ImportSummary):
        if not path.is_file():
            return
        dept_map = {d.codigo: d for d in Departamento.objects.all()}
        with path.open(encoding="utf-8-sig", newline="") as handle:
            for row in csv.DictReader(handle):
                dept = dept_map.get((row.get("departamento") or "").strip())
                EspecialidadeMedica.objects.update_or_create(
                    codigo=row["codigo"].strip(),
                    defaults={
                        "nome": row["nome"].strip(),
                        "descricao": row.get("descricao", "").strip(),
                        "activo": _bool(row.get("activo", "1")),
                        "duracao_consulta_minutos": int(row.get("duracao_consulta_minutos") or 30),
                        "ordem": int(row.get("ordem") or 0),
                        "departamento": dept,
                    },
                )
