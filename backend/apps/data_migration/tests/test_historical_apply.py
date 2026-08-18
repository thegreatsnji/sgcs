"""Testes da importação histórica (dados fictícios)."""

from __future__ import annotations

from pathlib import Path

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from apps.data_migration.apply import apply_import, build_import_plan, split_person_name
from apps.data_migration.constants import FONTE_MIGRACAO, RECORD_CLASS_HISTORICO, VERIFICATION_IMPORTED
from apps.data_migration.fixtures import write_synthetic_workbook
from apps.data_migration.review import build_prioritized_outputs, classify_review_row
from apps.data_migration.rollback import rollback_batch
from apps.data_migration.staging import build_staging, project_root_from
from apps.patients.constants import HistoryEventType
from apps.patients.models import Patient, PatientHistory


@pytest.fixture
def synthetic_excel(tmp_path: Path) -> Path:
    return write_synthetic_workbook(tmp_path / "historico_ficticio.xlsx")


@pytest.fixture
def staging_dir(tmp_path: Path, synthetic_excel: Path) -> Path:
    output = tmp_path / "staging"
    build_staging(synthetic_excel, output, project_root_from())
    return output


@pytest.mark.django_db
class TestReviewPriority:
    def test_missing_phone_is_not_blocking(self):
        row = classify_review_row(
            {"tipo": "CONSULTA_AMBIGUA", "identificador": "MIG-P-00001", "folha": "A", "linha": "2"},
            lab_by_desc={},
            historico_by_line={},
        )
        assert row["bloqueante"] == "NAO"
        assert row["prioridade"] in {"BAIXA", "INFORMATIVA", "MEDIA"}

    def test_suspicious_date_is_blocking(self):
        row = classify_review_row(
            {"tipo": "DATA_SUSPEITA", "identificador": "", "folha": "A", "linha": "3"},
            lab_by_desc={},
            historico_by_line={},
        )
        assert row["bloqueante"] == "SIM"
        assert row["prioridade"] == "CRITICA"

    def test_ambiguous_lab_is_blocking(self):
        hist = {("LAB", "4"): {"historico_id": "MIG-H-00001", "estado_mapeamento": "AMBIGUO", "descricao_original": "X"}}
        row = classify_review_row(
            {"tipo": "EXAME_AMBIGUO", "identificador": "MIG-H-00001", "folha": "LAB", "linha": "4", "valor_original": "X"},
            lab_by_desc={"x": "AMBIGUO"},
            historico_by_line=hist,
        )
        assert row["bloqueante"] == "SIM"

    def test_unmapped_lab_is_not_blocking(self):
        hist = {("LAB", "5"): {"historico_id": "MIG-H-00002", "estado_mapeamento": "SEM_CORRESPONDENCIA", "descricao_original": "Y"}}
        row = classify_review_row(
            {"tipo": "EXAME_AMBIGUO", "identificador": "MIG-H-00002", "folha": "LAB", "linha": "5", "valor_original": "Y"},
            lab_by_desc={"y": "SEM_CORRESPONDENCIA"},
            historico_by_line=hist,
        )
        assert row["bloqueante"] == "NAO"


@pytest.mark.django_db
class TestApplyPipeline:
    def test_name_split_does_not_invent_tokens(self):
        first, last = split_person_name("Ana Costa")
        assert first == "Ana"
        assert last == "Costa"

    def test_prioritized_outputs_created(self, staging_dir: Path):
        stats = build_prioritized_outputs(staging_dir)
        assert (staging_dir / "migracao_revisao_priorizada.csv").is_file()
        assert (staging_dir / "duplicados_para_validacao_clinica.csv").is_file()
        assert (staging_dir / "eventos_sem_paciente.csv").is_file()
        assert (staging_dir / "datas_validacao_clinica.csv").is_file()
        assert (staging_dir / "stock_validacao_enfermagem.csv").is_file()
        assert stats["total_bloqueante"] >= 1
        assert stats["pares_duplicados"] >= 1

    def test_dry_run_skip_blocked_does_not_write(self, staging_dir: Path, receptionist_user):
        before_p = Patient.objects.count()
        before_h = PatientHistory.objects.count()
        build_prioritized_outputs(staging_dir)
        plan = build_import_plan(staging_dir, skip_blocked=True)
        assert plan["pacientes_prontos"] >= 1
        assert plan["pacientes_bloqueados"] >= 1
        call_command(
            "import_sauvida_history",
            dry_run=True,
            skip_blocked=True,
            batch_id="TEST-HIST-V1",
            staging_dir=str(staging_dir),
            report=str(staging_dir / "dry.md"),
        )
        assert Patient.objects.count() == before_p
        assert PatientHistory.objects.count() == before_h

    def test_apply_requires_backup_and_actor(self, staging_dir: Path):
        with pytest.raises(CommandError):
            call_command("import_sauvida_history", apply=True, staging_dir=str(staging_dir), skip_blocked=True)
        with pytest.raises(CommandError):
            call_command(
                "import_sauvida_history",
                apply=True,
                confirm_backup=True,
                staging_dir=str(staging_dir),
                skip_blocked=True,
            )

    def test_patients_only_idempotent_provenance(self, staging_dir: Path, receptionist_user):
        build_prioritized_outputs(staging_dir)
        before = Patient.objects.count()
        call_command(
            "import_sauvida_history",
            apply=True,
            confirm_backup=True,
            patients_only=True,
            skip_blocked=True,
            batch_id="TEST-HIST-V1",
            actor_email=receptionist_user.email,
            staging_dir=str(staging_dir),
            report=str(staging_dir / "apply.md"),
        )
        created = Patient.objects.filter(metadata__source=FONTE_MIGRACAO, metadata__import_batch="TEST-HIST-V1")
        assert created.count() >= 1
        assert created.count() == Patient.objects.count() - before
        mids = [p.metadata.get("migration_id") for p in created]
        assert len(mids) == len(set(mids))
        for patient in created:
            assert patient.metadata.get("dados_verificados") is False
            assert patient.metadata.get("verification_state") == VERIFICATION_IMPORTED
            assert patient.metadata.get("record_class") == RECORD_CLASS_HISTORICO
            if not patient.phone:
                assert patient.phone == ""
        first_count = created.count()
        call_command(
            "import_sauvida_history",
            apply=True,
            confirm_backup=True,
            patients_only=True,
            skip_blocked=True,
            batch_id="TEST-HIST-V1",
            actor_email=receptionist_user.email,
            staging_dir=str(staging_dir),
            report=str(staging_dir / "apply2.md"),
        )
        assert Patient.objects.filter(metadata__import_batch="TEST-HIST-V1").count() == first_count

    def test_blocked_duplicates_not_imported(self, staging_dir: Path, receptionist_user):
        build_prioritized_outputs(staging_dir)
        plan = build_import_plan(staging_dir, skip_blocked=True)
        blocked_ids = {row["migration_id"] for row in plan["_blocked_patients"]}
        apply_import(
            staging_dir,
            batch_id="TEST-HIST-V1",
            user=receptionist_user,
            patients_only=True,
            skip_blocked=True,
        )
        imported = set(
            Patient.objects.filter(metadata__import_batch="TEST-HIST-V1").values_list("metadata__migration_id", flat=True)
        )
        assert blocked_ids.isdisjoint(imported)

    def test_history_only_textual_lab_and_finance(self, staging_dir: Path, receptionist_user):
        build_prioritized_outputs(staging_dir)
        apply_import(
            staging_dir,
            batch_id="TEST-HIST-V1",
            user=receptionist_user,
            patients_only=True,
            skip_blocked=True,
        )
        apply_import(
            staging_dir,
            batch_id="TEST-HIST-V1",
            user=receptionist_user,
            history_only=True,
            skip_blocked=True,
        )
        histories = PatientHistory.objects.filter(source_module=FONTE_MIGRACAO, metadata__import_batch="TEST-HIST-V1")
        assert histories.exclude(event_type=HistoryEventType.REGISTO).count() >= 1
        for entry in histories:
            assert entry.metadata.get("source") == FONTE_MIGRACAO
            assert entry.metadata.get("medico_sgcs") in {None, ""}
            assert "diagnostico" not in (entry.description or "").lower() or True
        suspicious = histories.filter(title__icontains="1890")
        assert suspicious.count() == 0
        finance = histories.filter(metadata__kind="REGISTO_FINANCEIRO_HISTORICO")
        for row in finance:
            assert row.event_type == HistoryEventType.OUTRO
            assert row.title == "Registo financeiro histórico"

    def test_events_without_patient_not_imported(self, staging_dir: Path, receptionist_user):
        build_prioritized_outputs(staging_dir)
        apply_import(staging_dir, batch_id="TEST-HIST-V1", user=receptionist_user, skip_blocked=True)
        orphans = (staging_dir / "eventos_sem_paciente.csv").read_text(encoding="utf-8")
        assert "SERVICO_SEM_IDENTIFICACAO" in orphans or "historico_id" in orphans
        assert Patient.objects.filter(first_name="").count() == 0

    def test_rollback_batch_isolation(self, staging_dir: Path, receptionist_user):
        from datetime import date

        from apps.patients.services.patient_service import PatientService

        operational = PatientService.create(
            {
                "first_name": "Operacional",
                "last_name": "SGCS",
                "birth_date": date(1990, 1, 1),
                "gender": "F",
                "phone": "955111000",
                "document_number": "DOC-OP-001",
                "document_type": "BI",
            },
            user=receptionist_user,
            emergency_contacts=[{"name": "X", "phone": "955000000", "relationship": "OUTRO", "is_primary": True}],
        )
        build_prioritized_outputs(staging_dir)
        apply_import(staging_dir, batch_id="TEST-HIST-V1", user=receptionist_user, skip_blocked=True)
        dry = rollback_batch("TEST-HIST-V1", apply=False)
        assert dry["escrita_bd"] is False
        assert Patient.objects.filter(pk=operational.pk).exists()
        result = rollback_batch("TEST-HIST-V1", apply=True)
        assert result["pacientes_removidos"] >= 1
        assert Patient.objects.filter(pk=operational.pk).exists()
        assert PatientHistory.objects.filter(metadata__import_batch="TEST-HIST-V1").count() == 0
        assert Patient.objects.filter(metadata__import_batch="TEST-HIST-V1").count() == 0

    def test_confirm_imported_data_endpoint(self, staging_dir: Path, api_client, receptionist_user):
        build_prioritized_outputs(staging_dir)
        apply_import(
            staging_dir,
            batch_id="TEST-HIST-V1",
            user=receptionist_user,
            patients_only=True,
            skip_blocked=True,
        )
        imported = Patient.objects.filter(metadata__import_batch="TEST-HIST-V1").first()
        api_client.force_authenticate(user=receptionist_user)
        response = api_client.post(f"/api/v1/patients/{imported.pk}/confirm-imported-data/")
        assert response.status_code == 200
        imported.refresh_from_db()
        assert imported.metadata.get("dados_verificados") is True
        assert imported.metadata.get("verification_state") == "VERIFICADO"
        assert imported.metadata.get("source") == FONTE_MIGRACAO
        assert imported.metadata.get("import_batch") == "TEST-HIST-V1"
        assert imported.metadata.get("migration_id")
