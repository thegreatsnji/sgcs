"""Gera documentação Sprint 17 a partir dos CSV."""

from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DOCS = ROOT.parent / "docs"

DEPT = {
    "ADM": "Administração",
    "DIR": "Direção",
    "REC": "Receção",
    "CONS-GER": "Consulta Geral",
    "ESP-MED": "Especialidades Médicas",
    "ENF": "Enfermagem",
    "LAB": "Laboratório",
    "ECO": "Ecografia",
    "MAT-PAR": "Maternidade e Parteira",
    "CIR": "Cirurgia",
}

SECTION_ORDER = [
    ("CONSULTA", "1. Consultas"),
    ("LABORATORIO", "2. Laboratório"),
    ("ECOGRAFIA", "3. Ecografia"),
    ("ENFERMAGEM", "4. Enfermagem"),
    ("PROCEDIMENTO", "5. Procedimentos"),
    ("CIRURGIA", "6. Cirurgia"),
    ("MATERNIDADE", "7. Maternidade"),
    ("MED_URGENCIA", "8. Medicamentos e materiais de urgência"),
    ("MATERIAL_CLINICO", "8. Medicamentos e materiais de urgência"),
    ("IMUNIZACAO", "8. Medicamentos e materiais de urgência"),
    ("DOCUMENTO", "9. Documentos e cartões"),
    ("CARTAO", "9. Documentos e cartões"),
    ("OBSERVACAO_CLINICA", "9. Documentos e cartões"),
]


def load_catalog() -> list[dict[str, str]]:
    with (DATA / "catalogo_servicos_sauvida.csv").open(encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def write_ficha():
    rows = load_catalog()
    by_section: dict[str, list[dict[str, str]]] = {}
    for r in rows:
        cat = r["categoria"].strip()
        section = next((label for key, label in SECTION_ORDER if key == cat), "Outros")
        by_section.setdefault(section, []).append(r)

    lines = [
        "# Ficha de validação de preços — Clínica SauVida",
        "",
        "**Sprint 17** — Documento para impressão e sessão presencial.",
        "",
        "Instruções:",
        "",
        "1. Para cada serviço, confirme o preço em FCFA (inteiro, sem cêntimos).",
        "2. Registe quem confirmou e a data.",
        "3. Use o campo observações para dúvidas ou variantes.",
        "4. Após a sessão, preencha `backend/data/precos_validacao_clinica.csv` e importe com o Administrador.",
        "",
        "---",
        "",
    ]
    for section in sorted(by_section.keys()):
        lines.append(f"## {section}")
        lines.append("")
        lines.append("| Código | Serviço | Departamento | Preço actual (referência) | Preço confirmado (FCFA) | Confirmado por | Data | Observações |")
        lines.append("|---|---|---|---:|---:|---|---|---|")
        for r in sorted(by_section[section], key=lambda x: x["nome"]):
            preco = r.get("preco_fcfa", "").strip() or "—"
            dept = DEPT.get(r.get("departamento", ""), r.get("departamento", ""))
            lines.append(
                f"| {r['codigo']} | {r['nome']} | {dept} | {preco} | | | | |"
            )
        lines.append("")

    (DOCS / "FICHA_VALIDACAO_PRECOS_CLINICA.md").write_text("\n".join(lines), encoding="utf-8")


def write_lab_alignment():
    servicos = {r["codigo"]: r for r in load_catalog()}
    lines = [
        "# Alinhamento laboratório ↔ catálogo de serviços",
        "",
        "O **Serviço** (`billing.Servico`) é a fonte oficial do preço. Campos legados nos tipos de exame mantêm-se nesta sprint.",
        "",
        "| Exame | Serviço associado | Preço do exame | Preço do serviço | Situação | Acção |",
        "|---|---|---:|---:|---|---|",
    ]
    with (DATA / "exames_laboratoriais_sauvida.csv").open(encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            codigo = row["codigo"]
            nome = row["nome"]
            svc_code = row.get("servico_codigo", "").strip()
            svc = servicos.get(svc_code)
            preco_svc = svc.get("preco_fcfa", "—") if svc else "—"
            if not svc_code:
                sit, act = "SEM SERVIÇO", "Associar manualmente após validação de preços"
            elif not svc:
                sit, act = "NECESSITA REVISÃO", f"Criar ou importar serviço {svc_code}"
            elif preco_svc == "REVISAR_COM_CLINICA":
                sit, act = "NECESSITA REVISÃO", "Confirmar preço do serviço na clínica"
            else:
                sit, act = "ALINHADO", "Executar `align_lab_services` após serviços na BD"
            lines.append(
                f"| {nome} ({codigo}) | {svc_code or '—'} | — | {preco_svc} | {sit} | {act} |"
            )
    lines.append("")
    lines.append("**Estratégia de transição:** novos pedidos laboratoriais devem usar `TipoExameLaboratorio.servico` quando definido; preços antigos em faturas não são recalculados.")
    (DOCS / "LAB_CATALOGO_ALIGNMENT.md").write_text("\n".join(lines), encoding="utf-8")


def write_import_doc():
    text = """# Importação de preços confirmados

## Ficheiro

`backend/data/precos_validacao_clinica.csv`

Colunas: `codigo`, `nome`, `categoria`, `departamento`, `preco_actual_fcfa`, `preco_confirmado_fcfa`, `confirmado_por`, `data_confirmacao`, `observacoes`.

## Comandos

```bash
python manage.py import_catalogo_sauvida \\
  --file backend/data/precos_validacao_clinica.csv \\
  --dry-run

python manage.py import_catalogo_sauvida \\
  --file backend/data/precos_validacao_clinica.csv \\
  --apply \\
  --update-existing \\
  --actor-email admin@sauvida.gw
```

## Regras

- Importa **apenas** linhas com `preco_confirmado_fcfa` válido (inteiro ≥ 0).
- Ignora linhas vazias ou sem preço confirmado.
- Não altera serviços fora do ficheiro.
- Regista histórico (`ServicoPrecoHistorico`) com origem `IMPORTACAO_VALIDADA`.
- Utilizador `--actor-email` deve ser Administrador.
- Transação atómica por execução; erros críticos abortam (sem `--skip-invalid`).
- Valores `REVISAR_COM_CLINICA` no catálogo original **nunca** são importados como confirmados.

## Relatório

O comando imprime resumo: confirmados, pendentes, ignorados, actualizados e avisos.
"""
    (DOCS / "IMPORTACAO_PRECOS_CONFIRMADOS.md").write_text(text, encoding="utf-8")


def write_pacote():
    text = """# Pacote de validação presencial — Sprint 17

Sessão com: Administrador, Directora, Rececionista, Médico, Laboratório.

## Objectivos

- Validar preços no ficheiro `precos_validacao_clinica.csv`.
- Percorrer fluxos críticos de faturação e laboratório.
- Registar problemas com gravidade e responsável.

## Checklist — Receção

- [ ] Pesquisar paciente
- [ ] Criar fatura
- [ ] Pesquisar serviço (ServiceSearchPicker)
- [ ] Adicionar serviço com preço confirmado
- [ ] Ver mensagem se preço não confirmado
- [ ] Pagamento total
- [ ] Pagamento parcial
- [ ] Emitir recibo
- [ ] Imprimir
- [ ] Consultar saldo
- [ ] Cancelar operação (com autorização)

## Checklist — Médico

- [ ] Consultar paciente
- [ ] Abrir consulta
- [ ] Solicitar exame
- [ ] Visualizar serviço associado ao exame
- [ ] Consultar resultados

## Checklist — Laboratório

- [ ] Receber pedido
- [ ] Verificar autorização
- [ ] Colheita
- [ ] Inserir resultado
- [ ] Validar
- [ ] Publicar

## Checklist — Director

- [ ] Consultar catálogo
- [ ] Consultar preços e histórico
- [ ] Consultar receitas
- [ ] Consultar relatórios (sem alterar preços)

## Registo de problemas

| Problema | Gravidade | Sugestão | Responsável | Estado |
|---|---|---|---|---|
| | | | | |
"""
    (DOCS / "PACOTE_VALIDACAO_CLINICA_SPRINT17.md").write_text(text, encoding="utf-8")


if __name__ == "__main__":
    write_ficha()
    write_lab_alignment()
    write_import_doc()
    write_pacote()
    print("docs ok")
