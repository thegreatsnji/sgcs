"""Catálogo SauVida V1 em ficheiro — sem escrita na BD."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

from apps.data_migration.paths import data_dir
from apps.data_migration.text import fold_for_match


@dataclass(frozen=True)
class CatalogItem:
    codigo: str
    nome: str
    categoria: str
    nome_fold: str


@dataclass
class SauvidaCatalog:
    services: list[CatalogItem]
    exams: list[CatalogItem]

    def find_service(self, description: str) -> list[tuple[CatalogItem, float]]:
        return _rank(description, self.services)

    def find_exam(self, description: str) -> list[tuple[CatalogItem, float]]:
        ranked = _rank(description, self.exams)
        if ranked:
            return ranked
        return _rank(description, [s for s in self.services if s.categoria.upper() == "LABORATORIO"])


def load_catalog(project_root: Path) -> SauvidaCatalog:
    base = data_dir(project_root)
    services_path = base / "releases" / "catalogo_sauvida_v1.csv"
    exams_path = base / "releases" / "exames_laboratoriais_sauvida_v1.csv"
    return SauvidaCatalog(
        services=_load_csv(services_path, name_field="nome", code_field="codigo", category_field="categoria"),
        exams=_load_csv(
            exams_path,
            name_field="nome",
            code_field="codigo",
            category_field="categoria_laboratorial",
        ),
    )


def _load_csv(path: Path, name_field: str, code_field: str, category_field: str) -> list[CatalogItem]:
    if not path.is_file():
        return []
    items: list[CatalogItem] = []
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            nome = (row.get(name_field) or "").strip()
            codigo = (row.get(code_field) or "").strip()
            if not nome or not codigo:
                continue
            items.append(
                CatalogItem(
                    codigo=codigo,
                    nome=nome,
                    categoria=(row.get(category_field) or "").strip(),
                    nome_fold=fold_for_match(nome),
                )
            )
    return items


def _rank(description: str, items: list[CatalogItem]) -> list[tuple[CatalogItem, float]]:
    from difflib import SequenceMatcher

    target = fold_for_match(description)
    if not target or not items:
        return []
    ranked: list[tuple[CatalogItem, float]] = []
    for item in items:
        if item.nome_fold == target:
            ranked.append((item, 1.0))
            continue
        ratio = SequenceMatcher(None, target, item.nome_fold).ratio()
        if target in item.nome_fold or item.nome_fold in target:
            ratio = max(ratio, 0.9)
        ranked.append((item, round(ratio, 3)))
    ranked.sort(key=lambda pair: pair[1], reverse=True)
    return ranked[:5]
