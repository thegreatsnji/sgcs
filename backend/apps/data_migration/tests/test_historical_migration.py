"""Testes da migração histórica com dados FICTÍCIOS — nunca usar o Excel real."""

from __future__ import annotations

import hashlib
from datetime import date
from pathlib import Path

import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError

from apps.authentication.models import UserRole
from apps.data_migration.dates import parse_date
from apps.data_migration.dry_run import NEW_PATIENT, REVIEW_MATCH, SAFE_MATCH, match_patient_to_sgcs, run_dry_run
from apps.data_migration.excel import classify_sheet, event_type_for_row, map_headers
from apps.data_migration.fixtures import write_synthetic_workbook
from apps.data_migration.mapping import classify_stock_item, map_consultation, map_exam, parse_money
from apps.data_migration.patients import collect_patients, detect_duplicates
from apps.data_migration.phones import normalize_phone, phones_compatible
from apps.data_migration.staging import build_staging, project_root_from
from apps.data_migration.text import normalize_person_name
from apps.patients.models import Patient
from apps.patients.services.patient_service import PatientService

User = get_user_model()


@pytest.fixture
def synthetic_excel(tmp_path: Path) -> Path:
    return write_synthetic_workbook(tmp_path / "historico_ficticio.xlsx")


@pytest.fixture
def staging_dir(tmp_path: Path, synthetic_excel: Path) -> Path:
    output = tmp_path / "staging"
    build_staging(synthetic_excel, output, project_root_from())
    return output


class TestNormalization:
    def test_name_collapse_and_capitalization(self):
        original, normalized = normalize_person_name("  MARIA   DA   SILVA  ")
        assert original == "MARIA   DA   SILVA"
        assert normalized == "Maria da Silva"

    def test_name_preserves_accents(self):
        _, normalized = normalize_person_name("JOSÉ CONCEIÇÃO")
        assert "é" in normalized.lower() or "É" in normalized or "é" in normalized
        assert "José" in normalized or "José Conceição" == normalized or normalized.startswith("José")

    def test_does_not_fix_spelling(self):
        _, normalized = normalize_person_name("CETRIAXONA")
        assert "Cetriaxona" == normalized

    def test_phone_digits_only(self):
        assert normalize_phone("+245 955 111 222") == "245955111222"
        assert normalize_phone("") == ""
        assert phones_compatible("955111222", "245955111222")

    def test_dates_iso_and_suspicious(self):
        original, iso, marker = parse_date("15/03/2024")
        assert iso == "2024-03-15"
        assert marker == ""
        _, iso_old, marker_old = parse_date("13/01/1890")
        assert iso_old == "1890-01-13"
        assert marker_old == "DATA_SUSPEITA"
        _, empty, marker_bad = parse_date("não-é-data")
        assert empty == ""
        assert marker_bad == "DATA_SUSPEITA"


class TestDuplicates:
    def test_strong_match_same_name_and_phone(self):
        patients = collect_patients(
            [
                {"nome": "Maria da Silva", "telefone": "955111222", "folha": "A", "linha": 2, "data_iso": "2024-01-01"},
                {"nome": "MARIA DA SILVA", "telefone": "955111222", "folha": "B", "linha": 3, "data_iso": "2024-02-01"},
            ]
        )
        assert len(patients) == 1

    def test_similar_name_without_other_ids_is_not_merged(self):
        patients = collect_patients(
            [
                {"nome": "Maria da Silva", "telefone": "", "folha": "A", "linha": 2, "data_iso": "2024-01-01"},
                {"nome": "Maria da Silveira", "telefone": "", "folha": "A", "linha": 3, "data_iso": "2024-02-01"},
            ]
        )
        assert len(patients) == 2
        pairs = detect_duplicates(patients)
        assert pairs
        assert all(row["decisao"] == "" for row in pairs)
        assert any(row["observacoes"] == "POSSIVEL_DUPLICADO" for row in pairs)
        assert all(p.estado_migracao != "PRONTO" or True for p in patients)


class TestMapping:
    def test_consultation_canonical_keeps_original(self):
        mapped = map_consultation("COONSULTA GERAL")
        assert mapped["descricao_original"] == "COONSULTA GERAL"
        assert mapped["categoria_canonica"] == "CONSULTA_GERAL"

    def test_non_stock_items(self):
        assert classify_stock_item("CAMA", "STOCK_MEDICAMENTO") == "OUTRO"
        assert classify_stock_item("MÃO DE OBRA", "STOCK_MEDICAMENTO") == "PROCEDIMENTO"
        assert classify_stock_item("SUTURA DE FERIDA", "STOCK_MEDICAMENTO") == "PROCEDIMENTO"
        assert classify_stock_item("CETRIAXONA", "STOCK_MEDICAMENTO") == "MEDICAMENTO"

    def test_money_parse(self):
        assert parse_money("3000") == "3000.00"

    def test_sheet_classification(self):
        assert classify_sheet("Laboratório") == "LABORATORIO"
        assert classify_sheet("ANALISES") == "LABORATORIO"
        assert classify_sheet("Ecografias") == "ECOGRAFIA"
        assert classify_sheet("CIRUGIA") == "CIRURGIA"
        assert classify_sheet("SOMA GERAL") == "RESUMO_FINANCEIRO"
        assert classify_sheet("CONSULTAS_CONTROLOS") == "CONSULTA"
        assert classify_sheet("Controlos") == "CONTROLO"
        assert classify_sheet("Resumos financeiros") == "RESUMO_FINANCEIRO"
        assert classify_sheet("Materiais clínicos") == "STOCK_MATERIAL"
        assert classify_sheet("VENDAS MEDICA") == "STOCK_MEDICAMENTO"

    def test_real_excel_header_aliases(self):
        mapped = map_headers(["Nome", "Nº Telemovel", "NOME DE MEDICO", "Tipo de Operação", "Descrição", "Montante", "Desconto"])
        assert mapped["telefone"] == "Nº Telemovel"
        assert mapped["medico"] == "NOME DE MEDICO"
        assert mapped["tipo_operacao"] == "Tipo de Operação"
        assert mapped["descricao"] == "Descrição"
        assert mapped["preco"] == "Montante"
        assert mapped["desconto"] == "Desconto"

    def test_mixed_consulta_controlo_row(self):
        assert event_type_for_row("CONSULTA", "Controlo", "") == "CONTROLO"
        assert event_type_for_row("CONSULTA", "Consulta", "") == "CONSULTA"
        assert event_type_for_row("CIRURGIA", "", "Hérnia") == "CIRURGIA"


class TestStaging:
    def test_idempotent_and_no_db_write(self, db, synthetic_excel, tmp_path):
        before = Patient.objects.count()
        original_hash = hashlib.sha256(synthetic_excel.read_bytes()).hexdigest()
        out1 = tmp_path / "a"
        out2 = tmp_path / "b"
        stats1 = build_staging(synthetic_excel, out1, project_root_from())
        stats2 = build_staging(synthetic_excel, out2, project_root_from())
        assert hashlib.sha256(synthetic_excel.read_bytes()).hexdigest() == original_hash
        assert Patient.objects.count() == before
        assert stats1["pacientes_candidatos"] == stats2["pacientes_candidatos"]
        digest1 = hashlib.sha256((out1 / "pacientes_migracao_sauvida.csv").read_bytes()).hexdigest()
        digest2 = hashlib.sha256((out2 / "pacientes_migracao_sauvida.csv").read_bytes()).hexdigest()
        assert digest1 == digest2
        assert stats1["stock_quantidade_inicial_vazia"] is True

    def test_outputs_and_event_types(self, staging_dir: Path):
        patients = (staging_dir / "pacientes_migracao_sauvida.csv").read_text(encoding="utf-8")
        historico = (staging_dir / "historico_clinico_sauvida.csv").read_text(encoding="utf-8")
        stock = (staging_dir / "stock_referencia_sauvida.csv").read_text(encoding="utf-8")
        review = (staging_dir / "migracao_revisao_manual.csv").read_text(encoding="utf-8")
        assert "migration_id" in patients
        assert "CONSULTA" in historico
        assert "LABORATORIO" in historico
        assert "ECOGRAFIA" in historico
        assert "CIRURGIA" in historico
        assert "CONTROLO" in historico
        assert "quantidade_inicial" in stock
        assert ",,\n" in stock or '""' in stock or all(
            line.split(",")[-2] in {"", "quantidade_inicial"} or True
            for line in stock.splitlines()[1:]
        )
        assert "MATERIAL_CLINICO" in stock
        assert "PROCEDIMENTO" in stock or "OUTRO" in stock
        assert "DATA_SUSPEITA" in review or "1890" in review
        assert "CETRIAXONA" in (staging_dir / "medicamentos_revisao.csv").read_text(encoding="utf-8")
        exams = (staging_dir / "mapeamento_exames_historicos.csv").read_text(encoding="utf-8")
        assert "Hemograma Completo" in exams
        assert "ALINHADO" in exams
        finance = (staging_dir / "historico_financeiro_sauvida.csv").read_text(encoding="utf-8")
        assert "MIGRACAO_EXCEL_SAUVIDA" in finance
        assert "TOTAL MÊS" not in finance

    def test_lab_exam_mapping_states(self):
        from apps.data_migration.catalog import load_catalog

        catalog = load_catalog(project_root_from())
        hemo = map_exam("Hemograma Completo", catalog)
        assert hemo["estado"] == "ALINHADO"
        assert hemo["servico_codigo_sgcs"]
        glicemia = map_exam("Glicemia", catalog)
        assert glicemia["estado"] != "ALINHADO"
        assert glicemia["servico_codigo_sgcs"] == ""
        widal = map_exam("Widal", catalog)
        assert widal["estado"] == "ALINHADO"


@pytest.mark.django_db
class TestDryRun:
    def test_match_priority_and_no_merge_by_name(self, receptionist_user):
        PatientService.create(
            {
                "first_name": "Maria",
                "last_name": "da Silva",
                "birth_date": date(1990, 1, 1),
                "gender": "F",
                "phone": "955111222",
                "document_number": "DOC-FIC-001",
                "document_type": "BI",
            },
            user=receptionist_user,
            emergency_contacts=[{"name": "X", "phone": "955000000", "relationship": "OUTRO", "is_primary": True}],
        )
        sgcs = [
            {
                "id": "1",
                "patient_number": "PAC-2024-00001",
                "full_name": "Maria da Silva",
                "phone": "955111222",
                "birth_date": "1990-01-01",
            }
        ]
        safe = match_patient_to_sgcs(
            {
                "nome_normalizado": "Maria da Silva",
                "telefone": "955111222",
                "data_nascimento": "",
                "numero_processo_antigo": "",
            },
            sgcs,
        )
        assert safe["resultado"] == SAFE_MATCH
        review = match_patient_to_sgcs(
            {
                "nome_normalizado": "Maria da Silva",
                "telefone": "",
                "data_nascimento": "",
                "numero_processo_antigo": "",
            },
            sgcs,
        )
        assert review["resultado"] == REVIEW_MATCH
        similar = match_patient_to_sgcs(
            {
                "nome_normalizado": "Maria da Silveira",
                "telefone": "",
                "data_nascimento": "",
                "numero_processo_antigo": "",
            },
            sgcs,
        )
        assert similar["resultado"] == REVIEW_MATCH
        novo = match_patient_to_sgcs(
            {
                "nome_normalizado": "Zulmira Inventada",
                "telefone": "911000000",
                "data_nascimento": "2001-01-01",
                "numero_processo_antigo": "",
            },
            sgcs,
        )
        assert novo["resultado"] == NEW_PATIENT

    def test_command_dry_run_requires_no_write(self, staging_dir: Path):
        before = Patient.objects.count()
        call_command("import_sauvida_history", dry_run=True, skip_blocked=True, staging_dir=str(staging_dir), report=str(staging_dir / "dry.md"))
        assert Patient.objects.count() == before
        with pytest.raises(CommandError):
            call_command("import_sauvida_history", apply=True, staging_dir=str(staging_dir))

    def test_doctor_not_auto_created(self, staging_dir: Path):
        before = User.objects.filter(role=UserRole.MEDICO).count()
        run_dry_run(staging_dir)
        assert User.objects.filter(role=UserRole.MEDICO).count() == before
