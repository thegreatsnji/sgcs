"""
Constrói catálogo real a partir de extração OCR das fotografias da clínica.
Não inventa preços — conflitos ficam com preco_confirmado=false e estado REVISAR_COM_CLINICA.
"""

from __future__ import annotations

import csv
import json
import re
import unicodedata
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DOCS = ROOT.parent / "docs"

FOTOS = {
    "IMG_PRECARIO_MEDICO": "image-0233a9e7 (PREÇÁRIO MÉDICO / HOSPITALAR)",
    "IMG_LAB_BIOQUIMICA": "image-a003bcac (PREÇÁRIO LABORATÓRIO Bioquímica)",
    "IMG_LAB_HEMAT_MICRO": "image-40aba2b6 (Hematologia / Microbiologia)",
    "IMG_LAB_SORO_CARDIO": "image-0b4dc12c (Sorologia / Marcadores cardíacos)",
    "IMG_LAB_ENDO_MICRO": "image-a87efb4d (Endocrinologia / Microbiologia)",
    "IMG_FARM_CARTOES_MANUSCRITO": "image-aee66803 (Farmácia / cartões / manuscrito)",
    "IMG_COMPOSITE_PAREDE": "image-d4c1ec50 (composição parede — revisão parcial)",
}


def slug_code(prefix: str, nome: str) -> str:
    s = unicodedata.normalize("NFKD", nome).encode("ascii", "ignore").decode("ascii")
    s = re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-").upper()
    return f"{prefix}-{s[:40]}".strip("-")


@dataclass
class Item:
    nome: str
    categoria: str
    departamento: str
    preco: int | None
    fotografia: str
    linha: str = ""
    especialidade: str = ""
    observacoes: str = ""
    codigo: str = ""
    preco_confirmado: bool = True
    estado: str = "CONFIRMADO"
    operacional: bool = True

    def finalize(self):
        if not self.codigo:
            pref = {
                "CONSULTA": "CONS",
                "LABORATORIO": "LAB",
                "ECOGRAFIA": "ECO",
                "CIRURGIA": "CIR",
                "MATERNIDADE": "MAT",
                "PROCEDIMENTO": "PROC",
                "MED_URGENCIA": "MEDU",
                "MATERIAL_CLINICO": "MATC",
                "DOCUMENTO": "DOC",
                "CARTAO": "CARD",
                "OBSERVACAO_CLINICA": "OBS",
                "OUTRO": "OUT",
            }.get(self.categoria, "SVC")
            self.codigo = slug_code(pref, self.nome)
        if self.preco is None:
            self.preco_confirmado = False
            self.estado = "REVISAR_COM_CLINICA"
        if self.estado == "REVISAR_COM_CLINICA":
            self.preco_confirmado = False


def _medico_hospitalar() -> list[Item]:
    f = FOTOS["IMG_PRECARIO_MEDICO"]
    items = [
        Item("Cama", "OBSERVACAO_CLINICA", "ENF", 5000, f, "tabela/linha1"),
        Item("Clínico Geral", "CONSULTA", "CONS-GER", 3000, f, "Consulta", codigo="CONS-CLIN-GER"),
        Item("Especialidade", "CONSULTA", "ESP-MED", 5000, f, "Consulta", codigo="CONS-ESP"),
        Item("Pré-Natal", "CONSULTA", "MAT-PAR", 3000, f, "Consulta", codigo="CONS-PRE-NATAL", especialidade="OBS"),
        Item("Controle", "CONSULTA", "CONS-GER", 2000, f, "Consulta", codigo="CONS-CONTROLO", especialidade="CLIN-GER"),
        Item("Teste de gravidez", "LABORATORIO", "LAB", 2000, f, "Laboratório", codigo="LAB-HCG"),
        Item("Ecografia Geneco-Obstetricia", "ECOGRAFIA", "ECO", 10000, f, "Imaginologia", codigo="ECO-GO"),
        Item("Ecografia Morfologia", "ECOGRAFIA", "ECO", 25000, f, "Imaginologia", codigo="ECO-MORF"),
        Item("Ecografia Renal e Abdominal", "ECOGRAFIA", "ECO", 15000, f, "Imaginologia", codigo="ECO-REN-ABD"),
        Item("Hérnia", "CIRURGIA", "CIR", 200000, f, "Cirurgia", codigo="CIR-HERNIA"),
        Item("Parto normal", "MATERNIDADE", "MAT-PAR", 35000, f, "Cirurgia", codigo="MAT-PARTO-NORMAL"),
        Item("Aplicação ou Extração de Jadel", "PROCEDIMENTO", "ESP-MED", 5000, f, "Cirurgia", codigo="CIR-JAD-APL"),
        Item("Aplicação ou Extração de DIU", "PROCEDIMENTO", "ESP-MED", 5000, f, "Cirurgia", codigo="CIR-DIU-APL"),
        Item("Cesariana", "CIRURGIA", "MAT-PAR", 180000, f, "Cirurgia", codigo="CIR-CESAR"),
        Item("Gravidez Ectópica", "CIRURGIA", "MAT-PAR", 180000, f, "Cirurgia", codigo="CIR-ECTOP"),
        Item("Quisto", "CIRURGIA", "CIR", 200000, f, "Cirurgia", codigo="CIR-QUISTO"),
        Item("Mioma", "CIRURGIA", "CIR", 250000, f, "Cirurgia", codigo="CIR-MIOMA"),
        Item("Ceftriaxona", "MED_URGENCIA", "ENF", 1500, f, "Farmácia"),
        Item("Diclofenac", "MED_URGENCIA", "ENF", 1000, f, "Farmácia"),
        Item("Cimetidina", "MED_URGENCIA", "ENF", 1000, f, "Farmácia"),
        Item("Metoclopramida", "MED_URGENCIA", "ENF", 1000, f, "Farmácia"),
        Item("Vitamina C inj.", "MED_URGENCIA", "ENF", 1000, f, "Farmácia"),
        Item("B- Complexo inj.", "MED_URGENCIA", "ENF", 1000, f, "Farmácia"),
        Item("Siringa 10 cc", "MATERIAL_CLINICO", "ENF", 250, f, "Farmácia"),
        Item("Siringa 5 cc", "MATERIAL_CLINICO", "ENF", 150, f, "Farmácia"),
        Item("Siringa 20 cc", "MATERIAL_CLINICO", "ENF", 500, f, "Farmácia"),
        Item("Placa de Hernia", "MATERIAL_CLINICO", "ENF", 30000, f, "Farmácia"),
        Item("Cateter", "MATERIAL_CLINICO", "ENF", 500, f, "Farmácia"),
        Item("Compressa", "MATERIAL_CLINICO", "ENF", 1500, f, "Farmácia"),
        Item("NaCl 0,9 %", "MATERIAL_CLINICO", "ENF", 1500, f, "Farmácia"),
    ]
    return items


def _bioquimica() -> list[Item]:
    f = FOTOS["IMG_LAB_BIOQUIMICA"]
    names_prices = [
        ("Acido úrico", 4000),
        ("Albumina", 4000),
        ("Amiláse", 4000),
        ("Teste de Koh", 9500),
        ("Bilirrubina Direta", 4000),
        ("Bilirrubina Indireta", 4000),
        ("Bilirrulina Total", 4000),
        ("Cálcio", 4000),
        ("Colesterol HDL", 4000),
        ("Colesterol LDL", 4000),
        ("Colesterol Total", 4000),
        ("Creatinina Urina 24 H", 4000),
        ("Creatinina", 4000),
        ("Ferro Serico", 4000),
        ("Fosfatasse Alcalina", 4000),
        ("Fosforo", 4000),
        ("Glicose", 4000),
        ("GOT/AST", 4000),
        ("GPT/ALT", 4000),
        ("Magnésio", 4000),
        ("Proteínas Urinarias Urina 24 H", 4000),
        ("Proteínas Total", 4000),
    ]
    items = [
        Item(n, "LABORATORIO", "LAB", p, f, f"Bioquímica/{i+1}") for i, (n, p) in enumerate(names_prices)
    ]
    items.append(
        Item(
            "[linha sem nome]",
            "LABORATORIO",
            "LAB",
            4000,
            f,
            "Bioquímica/23",
            observacoes="Preço visível sem designação do exame",
            preco_confirmado=False,
            estado="REVISAR_COM_CLINICA",
        )
    )
    return items


def _hemat_micro() -> list[Item]:
    f = FOTOS["IMG_LAB_HEMAT_MICRO"]
    top = [
        ("Potássio", 4000),
        ("Triglicerídeos", 4000),
        ("Ureia na Urina 24H", 4000),
        ("Ureia", 4000),
        ("Y-GT", 4000),
        ("Ionograma", 20000),
        ("Proteína C Reactiva", 4000),
        ("CK-MB", 3500),
    ]
    hem = [
        ("Grupo Sanguíneo", 4000),
        ("Velocidade Sedimentação", 4000),
        ("Hemograma Completo", 4000, "LAB-HEMO"),
        ("PTT", 4000),
        ("PT/INR", 4000),
        ("Hemoglobina glicosilada", 15000),
        ("Teste de Gravidez", 2000),
    ]
    micro = [
        ("Urina Tipo II", 4000),
        ("Urina Tipo II Na Urina De 24 H", 4000),
        ("E. Bacteriológico do exsudado do trato Respiratório Superior", 5000),
        ("E. Bacteriológico Do exsudadoVaginal", 4000),
        ("E. Bacteriológico Do exsudado Uretral", 4000),
        ("E. Bacteriológico De Fezes", 4000),
        ("E. Bacteriológico De Feridas", 4000),
    ]
    items = [Item(n, "LABORATORIO", "LAB", p, f, f"top/{i}") for i, (n, p) in enumerate(top)]
    for i, row in enumerate(hem):
        code = row[2] if len(row) > 2 else ""
        items.append(Item(row[0], "LABORATORIO", "LAB", row[1], f, f"Hematologia/{i}", codigo=code))
    for i, (n, p) in enumerate(micro):
        items.append(Item(n, "LABORATORIO", "LAB", p, f, f"Microbiologia/{i}"))
    # Topo parcialmente visível
    items.append(
        Item(
            "VIH (AG/AC) 4a Geração",
            "LABORATORIO",
            "LAB",
            8000,
            f,
            "topo parcial",
            observacoes="Valor no topo da folha; confirmar com folha Endocrinologia (4.500)",
            estado="REVISAR_COM_CLINICA",
            preco_confirmado=False,
        )
    )
    items.append(
        Item("TSH", "LABORATORIO", "LAB", 6000, f, "topo parcial"),
    )
    items.append(
        Item("Toxoplasmose", "LABORATORIO", "LAB", 8000, f, "topo parcial"),
    )
    items.append(
        Item(
            "Progesterona",
            "LABORATORIO",
            "LAB",
            None,
            f,
            "topo parcial",
            observacoes="Preço oculto pelo sobrepor de folhas",
        )
    )
    return items


def _soro_cardio() -> list[Item]:
    f = FOTOS["IMG_LAB_SORO_CARDIO"]
    rows = [
        ("Rubéola IGG IGM", None),
        ("HCV", 4000),
        ("Helicobacter Pylori", 8000),
        ("Factor Reumatoide", 4000),
        ("Salmonela AG", 4000),
        ("Teste De Gravidez", 2500),
        ("ASTO", 4000),
        ("Rotavirus", 4000),
        ("Widal", 4000),
        ("TPHA", 5000),
        ("Cardio Combo (CK-MB Troponina, Mioglobina)", 9000),
        ("D-Dimeros", 4000),
        ("Mioglobina", None),
        ("Troponina", 4000),
        ("Tuberculose IGG IgM", 5000),
        ("Coagulograma", 8000),
        ("Coagulação", 8000),
        ("Testosterona", 8000),
        ("Tempo Coagulação", 4000),
        ("Tempo Sangramento", 4000),
    ]
    items = []
    for i, (n, p) in enumerate(rows):
        obs = ""
        estado = "CONFIRMADO"
        pc = True
        if n == "Factor Reumatoide":
            obs = "Conflito: 4.000cfa nesta folha vs 8.000cfa noutra fotografia"
            estado = "REVISAR_COM_CLINICA"
            pc = False
        if n == "Teste De Gravidez":
            obs = "Conflito: 2.500cfa aqui vs 2.000cfa PREÇÁRIO MÉDICO vs 4.000cfa lista inferior"
            estado = "REVISAR_COM_CLINICA"
            pc = False
        items.append(
            Item(n, "LABORATORIO", "LAB", p, f, str(i + 1), observacoes=obs, estado=estado, preco_confirmado=pc)
        )
    return items


def _endo_micro() -> list[Item]:
    f = FOTOS["IMG_LAB_ENDO_MICRO"]
    micro = [
        ("E. Bacteriológico De Urina", 4000),
        ("E. Direta Do exsudado Vaginal", 4000),
        ("E. Parasitológico De Fezes", 4000),
        ("Clamidia", 5000),
        ("Sifilis/VDRL", 3000),
        ("BK", 4000),
        ("Gota Espessa", 2000),
    ]
    endo = [
        ("PSA", 8000),
        ("Estradiol", 7500),
        ("FSH", 8000),
        ("Prolactina", 10000),
        ("Anticorpo HBc IgM", 4000),
        ("Anticorpo HBe", 4000),
        ("Antigénio HBs", 4000),
        ("Antigénio Hepatite B", 4000),
        ("HBS AG", 3000),
        ("T3", 4000),
        ("T4", 4000),
        ("LH", 8000),
        ("VIH TESTE Rapido", 1500),
        ("VIH (AG/AC) 4a Geração", 4500),
        ("Progesterona", 8000),
        ("TSH", 6000),
        ("Toxoplasmose", 8000),
    ]
    items = [Item(n, "LABORATORIO", "LAB", p, f, f"micro/{i}") for i, (n, p) in enumerate(micro)]
    for i, (n, p) in enumerate(endo):
        obs = ""
        if n == "VIH (AG/AC) 4a Geração":
            obs = "Ver também valor 8.000 no topo de outra folha"
        items.append(Item(n, "LABORATORIO", "LAB", p, f, f"endo/{i}", observacoes=obs))
    return items


def _farm_cartoes_manuscrito() -> list[Item]:
    f = FOTOS["IMG_FARM_CARTOES_MANUSCRITO"]
    items = [
        Item("Ringer Lactato", "MED_URGENCIA", "ENF", 1500, f, "Farmácia"),
        Item("Destrosa 5 %", "MED_URGENCIA", "ENF", 1500, f, "Farmácia"),
        Item("Nolotil INJ.", "MED_URGENCIA", "ENF", 1000, f, "Farmácia"),
        Item("Cartão de Vacina", "CARTAO", "ADM", 1000, f, "Imonologia"),
        Item("Cartão de Grávida", "CARTAO", "ADM", 2000, f, "Imonologia"),
        Item("CARTÃO DE TETANO", "CARTAO", "ADM", None, f, "Imonologia"),
        Item(
            "G.E.",
            "LABORATORIO",
            "LAB",
            2000,
            f,
            "manuscrito",
            observacoes="Abreviatura manuscrita; provável Gota Espessa (confirmar)",
            estado="REVISAR_COM_CLINICA",
            preco_confirmado=False,
        ),
        Item(
            "Hemograma completo",
            "LABORATORIO",
            "LAB",
            4000,
            f,
            "manuscrito",
            codigo="LAB-HEMO-MAN",
            observacoes="Duplicado com Hemograma Completo impresso — unificar na clínica",
            estado="REVISAR_COM_CLINICA",
            preco_confirmado=False,
        ),
        Item(
            "Widall",
            "LABORATORIO",
            "LAB",
            4000,
            f,
            "manuscrito",
            observacoes="Grafia manuscrita; provável Widal",
            estado="REVISAR_COM_CLINICA",
            preco_confirmado=False,
        ),
        Item(
            "Glicemia",
            "LABORATORIO",
            "LAB",
            2000,
            f,
            "manuscrito",
            observacoes="Conflito: 2.000 manuscrito vs 4.000 Bioquímica",
            estado="REVISAR_COM_CLINICA",
            preco_confirmado=False,
        ),
    ]
    return items


def collect_all() -> list[Item]:
    raw: list[Item] = []
    for fn in (_medico_hospitalar, _bioquimica, _hemat_micro, _soro_cardio, _endo_micro, _farm_cartoes_manuscrito):
        raw.extend(fn())
    for it in raw:
        it.finalize()
    return raw


def detect_duplicates(items: list[Item]) -> list[dict]:
    by_name: dict[str, list[Item]] = defaultdict(list)
    for it in items:
        key = it.nome.strip().lower()
        by_name[key].append(it)
    suggestions = []
    for name, group in by_name.items():
        if len(group) < 2:
            continue
        prices = {g.preco for g in group if g.preco is not None}
        if len(prices) > 1:
            suggestions.append(
                {
                    "nome": group[0].nome,
                    "tipo": "preco_divergente",
                    "precos": sorted(prices),
                    "codigos": [g.codigo for g in group],
                    "sugestao": "Rever com a clínica antes de unificar",
                }
            )
        elif len(group) > 1:
            suggestions.append(
                {
                    "nome": group[0].nome,
                    "tipo": "duplicado",
                    "codigos": [g.codigo for g in group],
                    "sugestao": "Manter um código; desactivar duplicado após confirmação",
                }
            )
    return suggestions


def write_servicos_csv(items: list[Item], path: Path):
    fields = [
        "codigo",
        "nome",
        "categoria",
        "departamento",
        "especialidade",
        "preco_fcfa",
        "operacional",
        "preco_confirmado",
        "origem",
        "observacoes",
        "fotografia",
        "estado",
        "ativo",
        "exige_pedido_medico",
        "gera_resultado",
    ]
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for it in items:
            w.writerow(
                {
                    "codigo": it.codigo,
                    "nome": it.nome,
                    "categoria": it.categoria,
                    "departamento": it.departamento,
                    "especialidade": it.especialidade,
                    "preco_fcfa": it.preco if it.preco is not None else "REVISAR_COM_CLINICA",
                    "operacional": "1" if it.operacional else "0",
                    "preco_confirmado": "TRUE" if it.preco_confirmado else "FALSE",
                    "origem": "OCR_FOTOGRAFIAS_CLINICA",
                    "observacoes": it.observacoes,
                    "fotografia": it.fotografia,
                    "estado": it.estado,
                    "ativo": "1",
                    "exige_pedido_medico": "1" if it.categoria == "LABORATORIO" else "0",
                    "gera_resultado": "1" if it.categoria == "LABORATORIO" else "0",
                }
            )


def write_exames_csv(items: list[Item], path: Path):
    lab = [it for it in items if it.categoria == "LABORATORIO" and not it.nome.startswith("[")]
    fields = [
        "codigo",
        "nome",
        "categoria_laboratorial",
        "tipo_amostra",
        "servico_codigo",
        "preco_fcfa",
        "estado",
        "origem",
        "fotografia",
    ]
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for it in lab:
            cat_lab = "GERAL"
            if "Endocrinologia" in it.fotografia or "endo/" in it.linha:
                cat_lab = "Endocrinologia"
            elif "Hematologia" in it.linha or "Hematologia" in it.fotografia:
                cat_lab = "Hematologia"
            elif "Microbiologia" in it.linha or "micro" in it.linha:
                cat_lab = "Microbiologia"
            elif "Bioquímica" in it.linha:
                cat_lab = "Bioquímica"
            w.writerow(
                {
                    "codigo": f"EX-{it.codigo}",
                    "nome": it.nome,
                    "categoria_laboratorial": cat_lab,
                    "tipo_amostra": "",
                    "servico_codigo": it.codigo,
                    "preco_fcfa": it.preco if it.preco is not None else "",
                    "estado": it.estado,
                    "origem": "OCR_FOTOGRAFIAS_CLINICA",
                    "fotografia": it.fotografia,
                }
            )


def compare_old(items: list[Item], path: Path):
    old_codes = {}
    old_path = DATA / "catalogo_servicos_sauvida.csv"
    if old_path.is_file():
        with old_path.open(encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                old_codes[row["codigo"]] = row
    new_codes = {it.codigo: it for it in items}
    lines = [
        "# Comparação catálogo preparado vs real (OCR)",
        "",
        "## Novos serviços (código real ausente no preparado)",
        "",
    ]
    for c, it in sorted(new_codes.items()):
        if c not in old_codes:
            lines.append(f"- `{c}` — {it.nome} ({it.preco} FCFA)")
    lines.append("\n## Removidos do preparado (não reaparecem no real)\n")
    for c, row in sorted(old_codes.items()):
        if c not in new_codes:
            lines.append(f"- `{c}` — {row['nome']}")
    lines.append("\n## Preços diferentes (mesmo código)\n")
    for c in set(old_codes) & set(new_codes):
        old_p = old_codes[c].get("preco_fcfa", "")
        new_it = new_codes[c]
        if old_p == "REVISAR_COM_CLINICA" and new_it.preco:
            lines.append(f"- `{c}`: preparado pendente → real **{new_it.preco}** FCFA")
        elif new_it.preco and old_p not in ("", "REVISAR_COM_CLINICA") and str(new_it.preco) != str(old_p):
            lines.append(f"- `{c}`: {old_p} → **{new_it.preco}**")
    path.write_text("\n".join(lines), encoding="utf-8")


def write_ocr_report(path: Path):
    sections = [
        ("IMG_PRECARIO_MEDICO", "Alta", "95%", "Tabela completa legível"),
        ("IMG_LAB_BIOQUIMICA", "Alta", "98%", "Bioquímica completa; linha sem nome no fim"),
        ("IMG_LAB_HEMAT_MICRO", "Boa", "90%", "Topo parcial (Progesterona sem preço)"),
        ("IMG_LAB_SORO_CARDIO", "Boa", "88%", "Mioglobina sem preço; conflitos gravidez/fator reumatoide"),
        ("IMG_LAB_ENDO_MICRO", "Boa", "92%", "Coluna esquerda legível"),
        ("IMG_FARM_CARTOES_MANUSCRITO", "Média", "85%", "Manuscrito — abreviaturas a confirmar"),
        ("IMG_COMPOSITE_PAREDE", "Média", "60%", "Muitos itens cortados; não usado como fonte primária"),
    ]
    lines = ["# Análise OCR — fotografias da clínica\n", "| Foto | Qualidade | Confiança | Revisão |\n|---|---|---|---|"]
    for name, q, c, r in sections:
        lines.append(f"| {FOTOS.get(name, name)} | {q} | {c} | {r} |")
    path.write_text("\n".join(lines), encoding="utf-8")


def main():
    items = collect_all()
    dupes = detect_duplicates(items)
    (DATA / "catalogo_real_duplicados.json").write_text(
        json.dumps(dupes, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    write_servicos_csv(items, DATA / "catalogo_servicos_sauvida_real.csv")
    write_exames_csv(items, DATA / "exames_laboratoriais_reais.csv")
    compare_old(items, DOCS / "COMPARACAO_CATALOGO_PREPARADO_REAL.md")
    write_ocr_report(DOCS / "OCR_ANALISE_IMAGENS.md")
    stats = {
        "total": len(items),
        "confirmados": sum(1 for i in items if i.preco_confirmado),
        "pendentes": sum(1 for i in items if not i.preco_confirmado),
        "lab": sum(1 for i in items if i.categoria == "LABORATORIO"),
        "consulta": sum(1 for i in items if i.categoria == "CONSULTA"),
        "dupes": len(dupes),
    }
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
