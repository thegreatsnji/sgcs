"""Testes Fase 5: pacote de validação, decisões de revisão e alias (dados fictícios)."""

from __future__ import annotations

from pathlib import Path

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError
from openpyxl import Workbook

from apps.data_migration.apply import apply_import, build_import_plan
from apps.data_migration.constants import BATCH_INITIAL, BATCH_REVIEW, FONTE_MIGRACAO, PATIENT_REVIEW_MERGE
from apps.data_migration.fixtures import write_synthetic_workbook
from apps.data_migration.merge import alias_map_from_pairs, canonical_migration_id, record_alias
from apps.data_migration.review import build_prioritized_outputs
from apps.data_migration.review_packs import PACK_FILES, write_validation_pack
from apps.data_migration.staging import build_staging, project_root_from
from apps.patients.models import Patient, PatientHistory


@pytest.fixture
def staging_dir(tmp_path: Path) -> Path:
    excel = write_synthetic_workbook(tmp_path / "historico_ficticio.xlsx")
    output = tmp_path / "staging"
    build_staging(excel, output, project_root_from())
    build_prioritized_outputs(output)
    return output


def _write_xlsx(path: Path, sheet: str, headers: list[str], rows: list[list]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    wb = Workbook()
    ws = wb.active
    ws.title = sheet
    ws.append(headers)
    for row in rows:
        ws.append(row)
    wb.save(path)
    wb.close()


@pytest.mark.django_db
class TestValidationPack:
    def test_pack_files_created(self, staging_dir: Path):
        written = write_validation_pack(staging_dir)
        pack = staging_dir / "validation_pack"
        assert pack.is_dir()
        for name in PACK_FILES.values():
            assert (pack / name).is_file()
        assert Path(written["duplicados"]).name == "pacientes_duplicados_validacao.xlsx"


@pytest.mark.django_db
class TestReviewDecisions:
    def test_indeterminado_does_not_unlock(self, staging_dir: Path, receptionist_user):
        apply_import(staging_dir, batch_id="TEST-HIST-V1", user=receptionist_user, skip_blocked=True)
        dups = (staging_dir / "duplicados_para_validacao_clinica.csv").read_text(encoding="utf-8").splitlines()
        if len(dups) > 1:
            header = dups[0].split(",")
            idx = header.index("decisao") if "decisao" in header else -1
            if idx >= 0:
                cols = dups[1].split(",")
                cols[idx] = "INDETERMINADO"
                dups[1] = ",".join(cols)
                (staging_dir / "duplicados_para_validacao_clinica.csv").write_text("\n".join(dups) + "\n", encoding="utf-8")
        plan = build_import_plan(staging_dir, skip_blocked=True, reviewed_only=True)
        assert plan["merges_confirmados"] == 0
        assert plan["pacientes_desbloqueados"] == 0

    def test_pessoas_diferentes_unlocks_without_merge(self, staging_dir: Path, receptionist_user):
        apply_import(staging_dir, batch_id="TEST-HIST-V1", user=receptionist_user, skip_blocked=True)
        path = staging_dir / "duplicados_para_validacao_clinica.csv"
        if not path.is_file():
            pytest.skip("sem duplicados sintéticos")
        lines = path.read_text(encoding="utf-8").splitlines()
        header = lines[0].split(",")
        if "decisao" not in header:
            pytest.skip("csv sem coluna decisao")
        idx = header.index("decisao")
        out = [lines[0]]
        for line in lines[1:]:
            cols = line.split(",")
            if len(cols) > idx:
                cols[idx] = "PESSOAS_DIFERENTES"
            out.append(",".join(cols))
        path.write_text("\n".join(out) + "\n", encoding="utf-8")
        plan = build_import_plan(staging_dir, skip_blocked=True, reviewed_only=True)
        assert plan["pacientes_mantidos_separados"] >= 1
        assert plan["merges_confirmados"] == 0
        assert alias_map_from_pairs(plan["_duplicates"]) == {}

    def test_keep_textual_lab(self, staging_dir: Path, receptionist_user):
        apply_import(staging_dir, batch_id="TEST-HIST-V1", user=receptionist_user, skip_blocked=True)
        plan = build_import_plan(staging_dir, skip_blocked=True)
        amb = [ev for ev in plan["_blocked_events"] if ev.get("estado_mapeamento") == "AMBIGUO"]
        if not amb:
            pytest.skip("sem lab ambíguo no workbook sintético")
        desc = amb[0].get("descricao_original") or ""
        _write_xlsx(
            staging_dir / "laboratorio_validacao_historica.xlsx",
            "laboratorio",
            ["descricao_excel", "decisao"],
            [[desc, "MANTER_TEXTUAL"]],
        )
        review = build_import_plan(staging_dir, skip_blocked=True, reviewed_only=True)
        assert review["labs_mantidos_textuais"] >= 1
        assert review["labs_mapeados"] == 0

    def test_mapped_lab(self, staging_dir: Path, receptionist_user):
        apply_import(staging_dir, batch_id="TEST-HIST-V1", user=receptionist_user, skip_blocked=True)
        plan = build_import_plan(staging_dir, skip_blocked=True)
        amb = [ev for ev in plan["_blocked_events"] if ev.get("estado_mapeamento") == "AMBIGUO"]
        if not amb:
            pytest.skip("sem lab ambíguo no workbook sintético")
        desc = amb[0].get("descricao_original") or ""
        _write_xlsx(
            staging_dir / "laboratorio_validacao_historica.xlsx",
            "laboratorio",
            ["descricao_excel", "decisao", "exame_confirmado"],
            [[desc, "CONFIRMAR_MAPEAMENTO", "HEMOGRAMA"]],
        )
        review = build_import_plan(staging_dir, skip_blocked=True, reviewed_only=True)
        assert review["labs_mapeados"] >= 1

    def test_date_decision_does_not_auto_correct(self, staging_dir: Path, receptionist_user):
        apply_import(staging_dir, batch_id="TEST-HIST-V1", user=receptionist_user, skip_blocked=True)
        source = staging_dir / "datas_validacao_clinica.csv"
        original = source.read_text(encoding="utf-8") if source.is_file() else ""
        _write_xlsx(
            staging_dir / "validation_pack" / "datas_suspeitas_validacao.xlsx",
            "datas",
            ["migration_event_id", "decisao", "data_confirmada"],
            [["MIG-H-99999", "CORRIGIR_DATA", "2024-01-01"]],
        )
        build_import_plan(staging_dir, skip_blocked=True, reviewed_only=True)
        if source.is_file():
            assert source.read_text(encoding="utf-8") == original

    def test_doctor_mapping_counts_without_creating_users(self, staging_dir: Path, receptionist_user):
        apply_import(staging_dir, batch_id="TEST-HIST-V1", user=receptionist_user, skip_blocked=True)
        from django.contrib.auth import get_user_model

        before = get_user_model().objects.count()
        _write_xlsx(
            staging_dir / "medicos_validacao_historica.xlsx",
            "medicos",
            ["nome_historico", "utilizador_sgcs_sugerido", "decisao"],
            [["Dr. Paulo Mendes", "medico@test.gw", "MAPEAR_COM_MEDICO_SGCS"]],
        )
        review = build_import_plan(staging_dir, skip_blocked=True, reviewed_only=True)
        assert review["medicos_mapeados"] >= 1
        assert get_user_model().objects.count() == before

    def test_review_batch_refuses_initial_id(self, staging_dir: Path):
        with pytest.raises(CommandError):
            call_command(
                "import_sauvida_history",
                dry_run=True,
                reviewed_only=True,
                skip_blocked=True,
                batch_id=BATCH_INITIAL,
                staging_dir=str(staging_dir),
                report=str(staging_dir / "no.md"),
            )

    def test_second_review_dry_run_is_idempotent(self, staging_dir: Path, receptionist_user):
        apply_import(staging_dir, batch_id="TEST-HIST-V1", user=receptionist_user, skip_blocked=True)
        first = build_import_plan(staging_dir, skip_blocked=True, reviewed_only=True)
        second = build_import_plan(staging_dir, skip_blocked=True, reviewed_only=True)
        assert first["pacientes_prontos"] == second["pacientes_prontos"] == 0
        assert first["eventos_prontos"] == second["eventos_prontos"] == 0
        assert first["registos_ainda_bloqueados"] == second["registos_ainda_bloqueados"]


@pytest.mark.django_db
class TestMergeProvenance:
    def test_canonical_is_deterministic(self):
        assert canonical_migration_id("MIG-P-00002", "MIG-P-00001") == "MIG-P-00001"
        mapping = alias_map_from_pairs(
            [
                {
                    "paciente_a_id": "MIG-P-00002",
                    "paciente_b_id": "MIG-P-00001",
                    "decisao": PATIENT_REVIEW_MERGE,
                    "grupo": "G1",
                }
            ]
        )
        assert mapping == {"MIG-P-00002": "MIG-P-00001"}

    def test_alias_preserves_migration_id(self, receptionist_user, staging_dir: Path):
        apply_import(staging_dir, batch_id="TEST-HIST-V1", user=receptionist_user, patients_only=True, skip_blocked=True)
        canonical = Patient.objects.filter(metadata__import_batch="TEST-HIST-V1").first()
        original = canonical.metadata.get("migration_id")
        record_alias(
            canonical,
            alias_migration_id_value="MIG-P-ALIAS",
            grupo="G-TEST",
            actor=receptionist_user,
            batch_id=BATCH_REVIEW,
        )
        canonical.refresh_from_db()
        assert canonical.metadata.get("migration_id") == original
        assert "MIG-P-ALIAS" in (canonical.metadata.get("historical_aliases") or [])
        assert canonical.metadata.get("source") == FONTE_MIGRACAO
        assert PatientHistory.objects.filter(patient=canonical, title__icontains="Alias histórico").exists()
        assert Patient.objects.filter(pk=canonical.pk).exists()
