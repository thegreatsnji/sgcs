"""Testes do catálogo real extraído por OCR (fotografias)."""

import csv
from pathlib import Path

import pytest
from django.core.management import call_command

DATA = Path(__file__).resolve().parents[3] / "data"


@pytest.fixture
def real_catalog_path():
    path = DATA / "catalogo_servicos_sauvida_real.csv"
    assert path.is_file(), "Execute scripts/build_catalogo_real_from_ocr.py"
    return path


def test_csv_estrutura(real_catalog_path):
    with real_catalog_path.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) >= 100
    for row in rows:
        assert row["codigo"]
        assert row["nome"]
        assert row["categoria"]
        assert row["departamento"]


def test_sem_preco_inventado(real_catalog_path):
    with real_catalog_path.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["preco_confirmado"] == "FALSE":
                assert row["estado"] == "REVISAR_COM_CLINICA" or row["preco_fcfa"] == "REVISAR_COM_CLINICA"


def test_duplicados_json():
    import json

    path = DATA / "catalogo_real_duplicados.json"
    assert path.is_file()
    data = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(data, list)


@pytest.mark.django_db
def test_import_real_dry_run(real_catalog_path, seed_rbac):
    call_command(
        "import_catalogo_sauvida",
        f"--file={real_catalog_path}",
        "--dry-run",
        "--create-missing-relations",
        "--materialize-without-price",
        "--update-existing",
    )
