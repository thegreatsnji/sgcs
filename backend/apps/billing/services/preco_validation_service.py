"""Validação do ficheiro precos_validacao_clinica.csv (Sprint 18)."""

from __future__ import annotations

import csv
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Iterable

from apps.billing.clinic_scope import EXCLUDED_SERVICE_CATEGORIES, EXCLUDED_SERVICE_CODES
from apps.billing.constants import SERVICE_CATEGORY_IMPORT_ALIASES
from apps.billing.services.catalog_service import parse_preco_fcfa

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


@dataclass
class LinhaValidacao:
    linha: int
    codigo: str
    nome: str
    preco_confirmado: str
    confirmado_por: str
    data_confirmacao: str
    estado: str
    problema: str = ""


@dataclass
class RelatorioValidacaoPrecos:
    linhas: list[LinhaValidacao] = field(default_factory=list)
    total: int = 0
    validas: int = 0
    pendentes: int = 0
    invalidas: int = 0
    duplicadas: int = 0
    codigo_desconhecido: int = 0
    nao_aplicavel: int = 0

    @property
    def bloqueia_importacao(self) -> bool:
        return self.invalidas > 0 or self.duplicadas > 0 or self.codigo_desconhecido > 0


def _load_catalog_codes(catalog_path: Path) -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    if not catalog_path.is_file():
        return out
    with catalog_path.open(encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            code = row.get("codigo", "").strip()
            if code:
                out[code] = row
    return out


def _load_departments(dept_path: Path) -> set[str]:
    codes: set[str] = set()
    json_path = dept_path
    if json_path.suffix == ".csv" and not json_path.is_file():
        json_path = dept_path.parent / "departamentos_sauvida.json"
    if json_path.suffix == ".json" and json_path.is_file():
        import json

        data = json.loads(json_path.read_text(encoding="utf-8"))
        for item in data if isinstance(data, list) else data.get("departamentos", []):
            c = (item.get("codigo") or "").strip()
            if c:
                codes.add(c)
        return codes
    if dept_path.is_file() and dept_path.suffix == ".csv":
        with dept_path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames and "codigo" in reader.fieldnames:
                for row in reader:
                    c = row.get("codigo", "").strip()
                    if c:
                        codes.add(c)
    return codes


def _normalize_categoria(raw: str) -> str | None:
    key = raw.strip().upper()
    if key in EXCLUDED_SERVICE_CATEGORIES or key in ("INTERNAMENTO",):
        return None
    mapped = SERVICE_CATEGORY_IMPORT_ALIASES.get(key) or SERVICE_CATEGORY_IMPORT_ALIASES.get(raw.strip())
    return mapped


def _valid_date(value: str) -> bool:
    if not value or not DATE_RE.match(value.strip()):
        return False
    try:
        datetime.strptime(value.strip(), "%Y-%m-%d")
        return True
    except ValueError:
        return False


def validar_ficheiro_precos(
    validation_path: Path,
    *,
    catalog_path: Path | None = None,
    departamentos_path: Path | None = None,
) -> RelatorioValidacaoPrecos:
    catalog_path = catalog_path or validation_path.parent / "catalogo_servicos_sauvida.csv"
    departamentos_path = departamentos_path or validation_path.parent / "departamentos_sauvida.json"
    catalog = _load_catalog_codes(catalog_path)
    dept_codes = _load_departments(departamentos_path)

    rel = RelatorioValidacaoPrecos()
    seen_codes: dict[str, int] = {}

    with validation_path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        for idx, row in enumerate(reader, start=2):
            rel.total += 1
            codigo = (row.get("codigo") or "").strip()
            nome = (row.get("nome") or "").strip()
            categoria_raw = (row.get("categoria") or "").strip()
            departamento = (row.get("departamento") or "").strip()
            preco_conf = (row.get("preco_confirmado_fcfa") or "").strip()
            confirmado_por = (row.get("confirmado_por") or "").strip()
            data_conf = (row.get("data_confirmacao") or "").strip()

            problemas: list[str] = []
            estado = "PENDENTE"

            if codigo in EXCLUDED_SERVICE_CODES:
                estado = "NÃO APLICÁVEL"
                problemas.append("Código de farmácia comercial / não aplicável")
            elif _normalize_categoria(categoria_raw) is None and categoria_raw:
                estado = "NÃO APLICÁVEL"
                problemas.append("Categoria internamento ou não aplicável")

            if not codigo:
                estado = "INVÁLIDA"
                problemas.append("Código vazio")
            elif codigo in seen_codes:
                estado = "DUPLICADA"
                problemas.append(f"Duplicado (primeira ocorrência linha {seen_codes[codigo]})")
                rel.duplicadas += 1
            else:
                seen_codes[codigo] = idx

            if codigo and codigo not in catalog and estado not in ("DUPLICADA", "NÃO APLICÁVEL", "INVÁLIDA"):
                estado = "CÓDIGO DESCONHECIDO"
                problemas.append("Código ausente no catálogo de referência")
                rel.codigo_desconhecido += 1

            if codigo in catalog and nome:
                ref_nome = catalog[codigo].get("nome", "").strip()
                if ref_nome and ref_nome.lower() != nome.lower():
                    if estado == "PENDENTE":
                        problemas.append(f"Nome difere do catálogo (referência: {ref_nome})")

            if categoria_raw:
                cat = _normalize_categoria(categoria_raw)
                if cat is None and estado == "PENDENTE":
                    estado = "NÃO APLICÁVEL"
                elif cat is None:
                    pass
                elif codigo in catalog:
                    ref_cat = catalog[codigo].get("categoria", "").strip()
                    if ref_cat and cat != _normalize_categoria(ref_cat):
                        problemas.append(f"Categoria difere do catálogo ({ref_cat})")

            if departamento and dept_codes and departamento not in dept_codes:
                problemas.append(f"Departamento desconhecido: {departamento}")

            if not preco_conf:
                if estado == "PENDENTE":
                    estado = "PENDENTE"
                problemas.append("Preço confirmado em falta")
            else:
                try:
                    preco, pendente = parse_preco_fcfa(preco_conf)
                    if pendente or preco is None:
                        estado = "INVÁLIDA"
                        problemas.append("Preço marcado para revisão ou inválido")
                    else:
                        if not confirmado_por:
                            estado = "INVÁLIDA"
                            problemas.append("confirmado_por em falta")
                        if not _valid_date(data_conf):
                            estado = "INVÁLIDA"
                            problemas.append("data_confirmacao inválida (use AAAA-MM-DD)")
                        if estado == "PENDENTE" and not problemas:
                            estado = "VÁLIDA"
                except ValueError as exc:
                    estado = "INVÁLIDA"
                    problemas.append(str(exc))

            linha = LinhaValidacao(
                linha=idx,
                codigo=codigo or "—",
                nome=nome or "—",
                preco_confirmado=preco_conf or "—",
                confirmado_por=confirmado_por or "—",
                data_confirmacao=data_conf or "—",
                estado=estado,
                problema="; ".join(problemas) if problemas else "—",
            )
            rel.linhas.append(linha)

            if estado == "VÁLIDA":
                rel.validas += 1
            elif estado == "PENDENTE":
                rel.pendentes += 1
            elif estado == "INVÁLIDA":
                rel.invalidas += 1
            elif estado == "NÃO APLICÁVEL":
                rel.nao_aplicavel += 1

    return rel


def relatorio_markdown(rel: RelatorioValidacaoPrecos, titulo: str = "Validação de preços") -> str:
    lines = [
        f"# {titulo}",
        "",
        f"**Total de linhas:** {rel.total}",
        f"**Válidas:** {rel.validas} | **Pendentes:** {rel.pendentes} | **Inválidas:** {rel.invalidas} | "
        f"**Duplicadas:** {rel.duplicadas} | **Código desconhecido:** {rel.codigo_desconhecido} | "
        f"**Não aplicável:** {rel.nao_aplicavel}",
        "",
        "| Linha | Código | Serviço | Preço confirmado | Validador | Data | Estado | Problema |",
        "|---:|---|---|---:|---|---|---|---|",
    ]
    for l in rel.linhas:
        lines.append(
            f"| {l.linha} | {l.codigo} | {l.nome} | {l.preco_confirmado} | {l.confirmado_por} | "
            f"{l.data_confirmacao} | {l.estado} | {l.problema} |"
        )
    lines.append("")
    if rel.bloqueia_importacao:
        lines.append("**Importação bloqueada:** existem linhas inválidas, duplicadas ou códigos desconhecidos.")
    elif rel.validas == 0:
        lines.append("**Importação de preços:** nenhuma linha válida — apenas dry-run/materialização sem preço.")
    else:
        lines.append("**Importação de preços:** permitida após backup para linhas VÁLIDAS.")
    return "\n".join(lines)


def export_revisao_csv(
    validation_path: Path,
    rel: RelatorioValidacaoPrecos,
    dest: Path,
) -> bool:
    """Copia linhas corrigíveis (inválidas/duplicadas/desconhecidas) para revisão."""
    estados_revisao = {"INVÁLIDA", "DUPLICADA", "CÓDIGO DESCONHECIDO"}
    linhas_numeros = {l.linha for l in rel.linhas if l.estado in estados_revisao}
    if not linhas_numeros:
        return False

    with validation_path.open(encoding="utf-8-sig", newline="") as src:
        reader = csv.DictReader(src)
        fieldnames = reader.fieldnames or []
        rows_out = []
        for idx, row in enumerate(reader, start=2):
            if idx in linhas_numeros:
                rows_out.append(row)

    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("w", encoding="utf-8", newline="") as out:
        writer = csv.DictWriter(out, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows_out)
    return True
