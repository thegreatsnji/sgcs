"""Testes Fase 4: auditoria de batch, rollback, isolamento e revisão (dados fictícios)."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from apps.billing.models import Fatura, Pagamento, Recibo
from apps.data_migration.apply import apply_import, build_import_plan
from apps.data_migration.batch_audit import audit_batch
from apps.data_migration.blocked import classify_blocked_events
from apps.data_migration.constants import BATCH_INITIAL, FONTE_MIGRACAO
from apps.data_migration.fixtures import write_synthetic_workbook
from apps.data_migration.review import build_prioritized_outputs
from apps.data_migration.review_packs import write_review_workbooks
from apps.data_migration.rollback import rollback_batch
from apps.data_migration.staging import build_staging, project_root_from
from apps.finance.models import MovimentoFinanceiro
from apps.patients.constants import HistoryEventType
from apps.patients.models import Patient, PatientHistory
from apps.patients.services.patient_service import PatientService
from apps.pharmacy.models import MedicamentoUrgencia, MovimentoStockUrgencia


@pytest.fixture
def staging_dir(tmp_path: Path) -> Path:
    excel = write_synthetic_workbook(tmp_path / "historico_ficticio.xlsx")
    output = tmp_path / "staging"
    build_staging(excel, output, project_root_from())
    build_prioritized_outputs(output)
    return output


@pytest.mark.django_db
class TestBatchAuditAndRollback:
    def test_audit_and_rollback_reconcile_registo_plus_clinical(self, staging_dir: Path, receptionist_user):
        apply_import(staging_dir, batch_id="TEST-HIST-V1", user=receptionist_user, skip_blocked=True)
        stats = audit_batch("TEST-HIST-V1")
        assert stats["escrita_bd"] is False
        assert stats["pacientes"] >= 1
        assert stats["historicos"] == stats["historicos_registo_importacao"] + stats["historicos_clinicos"]
        assert stats["orfos"] == 0
        assert stats["migration_ids_duplicados"] == 0
        assert stats["provenance_incompleta_pacientes"] == 0
        assert stats["historicos_em_pacientes_externos"] == 0
        dry = rollback_batch("TEST-HIST-V1", apply=False)
        assert dry["historicos_a_remover"] == stats["historicos"]
        assert dry["historicos_registo_importacao"] == stats["historicos_registo_importacao"]
        assert dry["historicos_clinicos"] == stats["historicos_clinicos"]
        assert dry["historicos_em_pacientes_externos"] == 0
        assert dry["pacientes_a_remover"] == stats["pacientes"]

    def test_rollback_dry_run_ignores_operational_patient(self, staging_dir: Path, receptionist_user):
        operational = PatientService.create(
            {
                "first_name": "Operacional",
                "last_name": "SGCS",
                "birth_date": date(1990, 1, 1),
                "gender": "F",
                "phone": "955111000",
                "document_number": "DOC-OP-F4",
                "document_type": "BI",
            },
            user=receptionist_user,
            emergency_contacts=[{"name": "X", "phone": "955000000", "relationship": "OUTRO", "is_primary": True}],
        )
        apply_import(staging_dir, batch_id="TEST-HIST-V1", user=receptionist_user, skip_blocked=True)
        dry = rollback_batch("TEST-HIST-V1", apply=False)
        assert operational.pk not in list(
            Patient.objects.filter(metadata__import_batch="TEST-HIST-V1").values_list("pk", flat=True)
        )
        assert dry["historicos_em_pacientes_externos"] == 0

    def test_audit_command_json_no_write(self, staging_dir: Path, receptionist_user, tmp_path: Path):
        before = Patient.objects.count()
        apply_import(staging_dir, batch_id="TEST-HIST-V1", user=receptionist_user, patients_only=True, skip_blocked=True)
        report = tmp_path / "audit.md"
        call_command("audit_sauvida_history_batch", batch_id="TEST-HIST-V1", json=True, report_path=str(report))
        assert Patient.objects.count() == before + Patient.objects.filter(metadata__import_batch="TEST-HIST-V1").count()
        assert report.is_file()
        assert "SAUVIDA" not in report.read_text(encoding="utf-8") or "TEST-HIST-V1" in report.read_text(encoding="utf-8")


@pytest.mark.django_db
class TestFinancialAndStockIsolation:
    def test_apply_does_not_create_modern_finance_or_stock(self, staging_dir: Path, receptionist_user):
        before = {
            "f": Fatura.objects.count(),
            "p": Pagamento.objects.count(),
            "r": Recibo.objects.count(),
            "m": MovimentoFinanceiro.objects.count(),
            "s": MedicamentoUrgencia.objects.count(),
            "sm": MovimentoStockUrgencia.objects.count(),
        }
        apply_import(staging_dir, batch_id="TEST-HIST-V1", user=receptionist_user, skip_blocked=True)
        assert Fatura.objects.count() == before["f"]
        assert Pagamento.objects.count() == before["p"]
        assert Recibo.objects.count() == before["r"]
        assert MovimentoFinanceiro.objects.count() == before["m"]
        assert MedicamentoUrgencia.objects.count() == before["s"]
        assert MovimentoStockUrgencia.objects.count() == before["sm"]
        stats = audit_batch("TEST-HIST-V1")
        assert all(value == 0 for value in stats["financial_leakage"].values())
        assert all(value == 0 for value in stats["stock_leakage"].values())
        assert stats["tabelas_inesperadas"] == {}


@pytest.mark.django_db
class TestReviewedBatchIsolation:
    def test_reviewed_only_refuses_initial_batch_id(self, staging_dir: Path):
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

    def test_reviewed_only_without_decisions_imports_nothing(self, staging_dir: Path, receptionist_user):
        apply_import(
            staging_dir,
            batch_id="TEST-HIST-V1",
            user=receptionist_user,
            skip_blocked=True,
        )
        before_p = Patient.objects.count()
        before_h = PatientHistory.objects.count()
        plan = build_import_plan(staging_dir, skip_blocked=True, reviewed_only=True)
        assert plan["pacientes_prontos"] == 0
        assert plan["eventos_prontos"] == 0
        apply_import(
            staging_dir,
            batch_id="TEST-HIST-V1-REVIEW",
            user=receptionist_user,
            skip_blocked=True,
            reviewed_only=True,
        )
        assert Patient.objects.count() == before_p
        assert PatientHistory.objects.count() == before_h

    def test_duplicate_decision_unlocks_only_review_batch(self, staging_dir: Path, receptionist_user):
        apply_import(staging_dir, batch_id="TEST-HIST-V1", user=receptionist_user, skip_blocked=True)
        plan = build_import_plan(staging_dir, skip_blocked=True)
        blocked = plan["_blocked_patients"]
        if not blocked:
            pytest.skip("workbook sintético sem pacientes bloqueados")
        dup_path = staging_dir / "duplicados_para_validacao_clinica.csv"
        text = dup_path.read_text(encoding="utf-8")
        if "decisao" in text:
            lines = text.splitlines()
            header = lines[0].split(",")
            idx = header.index("decisao")
            out = [lines[0]]
            for line in lines[1:]:
                cols = line.split(",")
                if len(cols) > idx:
                    cols[idx] = "PESSOAS_DIFERENTES"
                out.append(",".join(cols))
            dup_path.write_text("\n".join(out) + "\n", encoding="utf-8")
        review_plan = build_import_plan(staging_dir, skip_blocked=True, reviewed_only=True)
        assert review_plan["reviewed_only"] is True
        for row in review_plan["_ready_patients"]:
            assert not Patient.objects.filter(metadata__migration_id=row["migration_id"]).exists()


@pytest.mark.django_db
class TestBlockedClassificationAndPacks:
    def test_blocked_events_have_categories(self, staging_dir: Path):
        plan = build_import_plan(staging_dir, skip_blocked=True)
        classified = classify_blocked_events(
            plan["_blocked_events"],
            blocked_patients={row.get("migration_id") for row in plan["_blocked_patients"]},
            date_decision=plan["_date_decision"],
        )
        assert classified["total"] == len(plan["_blocked_events"])
        assert classified["desbloqueaveis_apos_duplicados"] <= classified["total"]

    def test_review_workbooks_created(self, staging_dir: Path):
        written = write_review_workbooks(staging_dir)
        for key in ("duplicados", "eventos_bloqueados", "laboratorio", "medicos", "stock", "datas"):
            assert Path(written[key]).is_file()
        assert "validation_pack" in written["duplicados"]


@pytest.mark.django_db
class TestConfirmationAndReceptionUpdate:
    def test_reception_update_preserves_provenance(self, staging_dir: Path, receptionist_user, api_client):
        apply_import(
            staging_dir,
            batch_id="TEST-HIST-V1",
            user=receptionist_user,
            patients_only=True,
            skip_blocked=True,
        )
        imported = Patient.objects.filter(metadata__import_batch="TEST-HIST-V1").first()
        mid = imported.metadata.get("migration_id")
        api_client.force_authenticate(user=receptionist_user)
        response = api_client.patch(
            f"/api/v1/patients/{imported.pk}/",
            {"phone": "+245955888777", "address_city": "Bissau", "gender": "F", "birth_date": "02/02/1991"},
            format="json",
        )
        assert response.status_code in {200, 201}
        imported.refresh_from_db()
        assert imported.metadata.get("source") == FONTE_MIGRACAO
        assert imported.metadata.get("import_batch") == "TEST-HIST-V1"
        assert imported.metadata.get("migration_id") == mid
        assert imported.phone
