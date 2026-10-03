"""Relatórios markdown sem dados pessoais identificáveis."""

from __future__ import annotations

from datetime import date
from pathlib import Path


def _table(stats: dict, keys: list[tuple[str, str]]) -> str:
    lines = ["| Métrica | Valor |", "| --- | --- |"]
    for key, label in keys:
        lines.append(f"| {label} | {stats.get(key, 0)} |")
    return "\n".join(lines)


AUDIT_KEYS = [
    ("folhas", "Folhas analisadas"),
    ("linhas_totais", "Linhas totais"),
    ("pacientes_candidatos", "Pacientes candidatos"),
    ("nomes_unicos_normalizados", "Nomes únicos normalizados"),
    ("pacientes_com_telefone", "Pacientes com telefone"),
    ("pacientes_com_residencia", "Pacientes com residência"),
    ("pacientes_incompletos", "Pacientes com dados identificativos em falta"),
    ("pacientes_revisao", "Pacientes a rever manualmente"),
    ("duplicados_exactos", "Duplicados exactos (nível A)"),
    ("duplicados_nivel_b", "Pares a rever (nível B)"),
    ("possiveis_duplicados", "Possíveis duplicados (nível C)"),
    ("pares_duplicados", "Pares de duplicados (todos os níveis)"),
    ("formulas", "Células com fórmula"),
    ("erros_excel", "Erros Excel (#REF!, …)"),
    ("eventos_historicos", "Eventos históricos extraídos"),
    ("datas_suspeitas", "Datas suspeitas"),
    ("datas_malformadas", "Datas malformadas"),
    ("datas_fora_periodo_dominante", "Datas fora do período dominante"),
    ("registos_invalidos", "Registos inválidos/rejeitados"),
    ("itens_revisao", "Itens para revisão manual"),
]


DRY_RUN_KEYS = [
    ("linhas_analisadas", "Linhas analisadas"),
    ("pacientes_candidatos", "Pacientes candidatos"),
    ("pacientes_novos", "Pacientes novos (estimativa)"),
    ("correspondencias_seguras", "Correspondências seguras com SGCS"),
    ("possiveis_duplicados_sgcs", "Possíveis duplicados SGCS"),
    ("registos_incompletos", "Registos incompletos"),
    ("eventos_historicos", "Eventos históricos"),
    ("consultas", "Consultas"),
    ("controlos", "Controlos"),
    ("laboratorio", "Laboratório"),
    ("laboratorio_mapeado_alinhado", "Eventos lab. ALINHADO"),
    ("laboratorio_mapeado_possivel", "Eventos lab. POSSIVEL"),
    ("laboratorio_mapeado_ambiguo", "Eventos lab. AMBIGUO"),
    ("laboratorio_sem_correspondencia", "Eventos lab. SEM_CORRESPONDENCIA"),
    ("ecografias", "Ecografias"),
    ("cirurgias", "Cirurgias"),
    ("registos_financeiros", "Registos financeiros históricos"),
    ("medicamentos_materiais", "Candidatos stock de referência"),
    ("registos_revisao", "Registos para revisão"),
    ("registos_ignorados", "Registos rejeitados (sem paciente/descrição/erro)"),
    ("medicos_historicos", "Médicos encontrados"),
    ("medicos_match_confirmado", "Médicos MATCH_CONFIRMADO"),
    ("medicos_possivel_match", "Médicos POSSIVEL_MATCH"),
    ("itens_ignorados", "Itens ignorados"),
    ("pacientes_prontos", "Pacientes a criar"),
    ("pacientes_associar", "Pacientes a associar"),
    ("pacientes_bloqueados", "Pacientes bloqueados"),
    ("eventos_prontos", "Eventos a importar"),
    ("eventos_bloqueados", "Eventos bloqueados"),
    ("laboratorio_estruturado", "Laboratório estruturado"),
    ("laboratorio_textual", "Laboratório textual"),
    ("financeiro_historico_pronto", "Financeiro histórico"),
    ("datas_bloqueadas", "Datas bloqueadas"),
]


def write_audit_report(path: Path, stats: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    sheets = stats.get("folhas_nomes") or []
    sheet_lines = "\n".join(f"- {name}" for name in sheets) or "- (nenhuma)"
    body = f"""# Auditoria do Excel histórico SauVida

**Data:** {date.today().isoformat()}  
**Fonte:** `{stats.get("fonte", "MIGRACAO_EXCEL_SAUVIDA")}`  
**Hash parcial do ficheiro (não PII):** `{stats.get("source_hash", "")}`

Este relatório contém **apenas métricas agregadas**. Não inclui nomes de pacientes.

## Folhas

{sheet_lines}

## Métricas

{_table(stats, AUDIT_KEYS)}

## Eventos por tipo

{_table(stats, [
    ("consultas", "Consultas"),
    ("controlos", "Controlos"),
    ("laboratorio", "Exames laboratoriais"),
    ("ecografias", "Ecografias"),
    ("cirurgias", "Cirurgias"),
    ("eventos_outro", "Outros eventos"),
    ("registos_financeiros", "Registos financeiros"),
    ("medicamentos_candidatos", "Medicamentos candidatos"),
    ("materiais_candidatos", "Materiais clínicos candidatos"),
    ("procedimentos_em_vendas", "Procedimentos misturados em vendas"),
    ("grupos_medicamentos_revisao", "Grupos de medicamentos para confirmação"),
    ("medicos", "Médicos encontrados"),
    ("lab_descricoes_unicas", "Descrições laboratoriais únicas"),
    ("lab_desc_alinhado", "Lab. descrições ALINHADO"),
    ("lab_desc_possivel", "Lab. descrições POSSIVEL"),
    ("lab_desc_ambiguo", "Lab. descrições AMBIGUO"),
    ("lab_desc_sem_correspondencia", "Lab. descrições SEM_CORRESPONDENCIA"),
    ("itens_revisao", "Itens para revisão manual"),
])}

## Qualidade de datas

{_table(stats, [
    ("data_minima", "Data válida mais antiga"),
    ("data_maxima", "Data válida mais recente"),
    ("ano_dominante", "Ano dominante"),
    ("datas_malformadas", "Datas malformadas"),
    ("datas_suspeitas", "Datas suspeitas"),
    ("datas_fora_periodo_dominante", "Fora do período dominante (±1 ano)"),
])}

## Notas

- O Excel original não foi modificado.
- Totais de folhas financeiras não foram convertidos em transações individuais.
- `quantidade_inicial` de stock permanece vazia.
"""
    path.write_text(body, encoding="utf-8")


def write_dry_run_report(path: Path, stats: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    body = f"""# Dry-run da migração histórica SauVida

**Data:** {date.today().isoformat()}  
**Fonte:** `{stats.get("fonte", "MIGRACAO_EXCEL_SAUVIDA")}`  
**Escrita na BD:** {'sim' if stats.get('escrita_bd') else 'não'}  
**`--apply`:** {'activado' if stats.get('apply') else 'desactivado'}

Apenas estatísticas agregadas. Sem nomes reais.

{_table(stats, DRY_RUN_KEYS)}

## Correspondência com SGCS

Prioridade usada (nunca fusão automática só por nome):

1. número de processo antigo exacto;
2. telefone exacto + nome compatível;
3. nome exacto + data de nascimento;
4. nome exacto sem outros identificadores → REVISAR;
5. nome semelhante → REVISAR.
"""
    path.write_text(body, encoding="utf-8")
