"""Importação histórica SauVida: dry-run ou apply por lote."""

from __future__ import annotations

from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from apps.data_migration.apply import apply_import, build_import_plan
from apps.data_migration.constants import BATCH_INITIAL, FONTE_MIGRACAO
from apps.data_migration.paths import default_output_dir, docs_dir, project_root_from
from apps.data_migration.reports import write_dry_run_report
from apps.data_migration.review import build_prioritized_outputs


class Command(BaseCommand):
    help = "Dry-run ou importação histórica SauVida (pacientes/histórico) com proveniência."

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true", help="Apenas plano. Sem escrita.")
        parser.add_argument("--apply", action="store_true", help="Executa a importação (requer --confirm-backup).")
        parser.add_argument("--patients-only", action="store_true")
        parser.add_argument("--history-only", action="store_true")
        parser.add_argument("--skip-blocked", action="store_true")
        parser.add_argument("--reviewed-only", action="store_true", help="Apenas itens com decisão clínica confirmada (batch de revisão).")
        parser.add_argument("--batch-id", type=str, default="SAUVIDA-HIST-V1")
        parser.add_argument("--actor-email", type=str, default="")
        parser.add_argument("--staging-dir", type=str, default="")
        parser.add_argument("--report", type=str, default="")
        parser.add_argument("--report-path", type=str, default="")
        parser.add_argument(
            "--confirm-backup",
            action="store_true",
            help="Confirma que existe backup PostgreSQL válido antes de --apply.",
        )

    def handle(self, *args, **options):
        if options["apply"] and options["dry_run"]:
            raise CommandError("Indique --apply ou --dry-run, não ambos.")
        if options["patients_only"] and options["history_only"]:
            raise CommandError("Indique --patients-only ou --history-only, não ambos.")

        root = project_root_from()
        staging_dir = Path(options["staging_dir"] or default_output_dir(root))
        if not staging_dir.is_dir():
            raise CommandError(f"Pasta de staging não encontrada: {staging_dir}.")
        if not (staging_dir / "pacientes_migracao_sauvida.csv").is_file():
            raise CommandError("CSV de pacientes em falta.")

        build_prioritized_outputs(staging_dir)
        skip_blocked = bool(options["skip_blocked"])
        reviewed_only = bool(options["reviewed_only"])
        batch_id = options["batch_id"]
        if reviewed_only and batch_id == BATCH_INITIAL:
            raise CommandError(
                "Registos revistos não podem reutilizar SAUVIDA-HIST-V1. "
                "Use --batch-id SAUVIDA-HIST-V1-REVIEW."
            )
        report_path = Path(
            options["report_path"] or options["report"] or (docs_dir(root) / "MIGRACAO_HISTORICA_DRY_RUN.md")
        )

        if not options["apply"]:
            plan = build_import_plan(staging_dir, skip_blocked=skip_blocked, reviewed_only=reviewed_only)
            public = {key: value for key, value in plan.items() if not key.startswith("_")}
            public.update({"escrita_bd": False, "apply": False, "import_batch": batch_id})
            write_dry_run_report(report_path, public)
            self._print_plan(public, report_path)
            return

        if not options["confirm_backup"]:
            raise CommandError(
                "Recusado: --apply exige --confirm-backup depois de um dump PostgreSQL válido "
                "(ver docs/MIGRACAO_HISTORICA_BACKUP.md)."
            )
        email = (options["actor_email"] or "").strip()
        if not email:
            raise CommandError("--actor-email é obrigatório para --apply.")
        User = get_user_model()
        try:
            user = User.objects.get(email__iexact=email, is_active=True)
        except User.DoesNotExist as exc:
            raise CommandError(f"Utilizador activo não encontrado: {email}") from exc

        stats = apply_import(
            staging_dir,
            batch_id=batch_id,
            user=user,
            patients_only=options["patients_only"],
            history_only=options["history_only"],
            skip_blocked=skip_blocked,
            reviewed_only=reviewed_only,
        )
        write_dry_run_report(report_path, stats)
        self._print_plan(stats, report_path)

    def _print_plan(self, stats: dict, report_path: Path) -> None:
        self.stdout.write(self.style.MIGRATE_HEADING("=== import_sauvida_history ==="))
        self.stdout.write(f"Fonte: {FONTE_MIGRACAO}")
        self.stdout.write(f"Lote: {stats.get('import_batch', '')}")
        self.stdout.write(f"Escrita na BD: {'sim' if stats.get('escrita_bd') else 'não'}")
        for key, label in (
            ("pacientes_prontos", "Pacientes a criar"),
            ("pacientes_associar", "Pacientes a associar"),
            ("pacientes_bloqueados", "Pacientes bloqueados"),
            ("pacientes_criados", "Pacientes criados"),
            ("eventos_prontos", "Eventos a importar"),
            ("eventos_bloqueados", "Eventos bloqueados"),
            ("consultas_prontas", "Consultas prontas"),
            ("controlos_prontos", "Controlos prontos"),
            ("laboratorio_estruturado", "Laboratório alinhado/estruturado"),
            ("laboratorio_textual", "Laboratório textual"),
            ("ecografias_prontas", "Ecografias"),
            ("cirurgias_prontas", "Cirurgias"),
            ("financeiro_historico_pronto", "Financeiro histórico"),
            ("datas_bloqueadas", "Datas bloqueadas"),
            ("eventos_desbloqueaveis_apos_duplicados", "Eventos desbloqueáveis após duplicados"),
            ("pacientes_desbloqueados", "Pacientes desbloqueados"),
            ("merges_confirmados", "Merges confirmados (MESMA_PESSOA)"),
            ("pacientes_mantidos_separados", "Pacientes mantidos separados"),
            ("eventos_desbloqueados", "Eventos desbloqueados"),
            ("labs_mapeados", "Labs mapeados"),
            ("labs_mantidos_textuais", "Labs mantidos textuais"),
            ("datas_corrigidas", "Datas corrigidas (clínica)"),
            ("medicos_mapeados", "Médicos mapeados"),
            ("registos_ainda_bloqueados", "Registos ainda bloqueados"),
            ("itens_ignorados", "Itens ignorados"),
            ("eventos_sem_paciente", "Eventos sem paciente"),
        ):
            if key in stats:
                self.stdout.write(f"{label}: {stats.get(key, 0)}")
        self.stdout.write(f"Relatório: {report_path}")
