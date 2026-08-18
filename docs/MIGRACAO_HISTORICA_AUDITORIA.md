# Auditoria do Excel histórico SauVida

**Data:** 2026-08-17  
**Fonte:** `MIGRACAO_EXCEL_SAUVIDA`  
**Hash SHA256 do Excel original:** `bfd987eec4a82c454d1a4519d460ef64fcad16b91dcb47af95fe6a6847ce6822`  
**Tamanho:** 115869 bytes (inalterado após a pipeline)

Este relatório contém **apenas métricas agregadas**. Não inclui nomes, telefones nem outros dados identificáveis.

O Excel original **não está no Git**. Cópia de trabalho em `backend/data/private/sauvida_migration/` (gitignored). A pipeline é só de leitura sobre o `.xlsx`.

```bash
python backend/scripts/audit_sauvida_historical_excel.py --input backend/data/private/sauvida_migration/sauvida_historico_original.xlsx
python backend/scripts/build_sauvida_historical_staging.py --input backend/data/private/sauvida_migration/sauvida_historico_original.xlsx
```

## Folhas analisadas (13)

- LABORATORIO
- CONSULTAS_CONTROLOS
- ECOGRAFIA
- CIRUGIA (grafia da fonte; classificada como cirurgia)
- VENDAS
- SOMA GERAL (resumo; **não** convertido em transações)
- CONSULTAS ADULTOS AGOSTO
- CONSULTAS PED
- CONTROLOS
- ANALISES (classificada como laboratório)
- ECOGRAFIA AGOSTO
- CIRURGIA AGOSTO
- VENDAS MEDICA

## Pacientes (agregado)

| Métrica | Valor |
| --- | --- |
| Linhas de origem (folha, não vazias, excl. cabeçalho) | 651 |
| Pacientes candidatos | 194 |
| Nomes únicos normalizados | 191 |
| Duplicados exactos (nível A, mesmo nome+telefone) | 0 (já colapsados na chave) |
| Pares nível B (`REVISAR_DUPLICADO`) | 1 |
| Possíveis duplicados (nível C, só nome) | 22 |
| Pares de duplicados (todos os níveis) | 23 |
| Com telefone | 13 |
| Com residência | 0 |
| Dados identificativos em falta (`DADOS_INSUFICIENTES`) | 181 |
| A rever (`revisar=SIM`) | 188 |
| Prontos sem revisão | 6 |

Nunca foi feita fusão automática só por semelhança de nome.

## Eventos históricos

| Tipo | Total |
| --- | --- |
| CONSULTA | 148 |
| CONTROLO | 18 |
| LABORATORIO | 137 |
| ECOGRAFIA | 58 |
| CIRURGIA | 60 |
| OUTRO | 0 |
| **Total eventos** | **421** |
| Com relação a paciente candidato | 248 |
| Sem paciente identificável | 173 |

Cada evento preserva descrição original, data original, médico (quando existe), preço, desconto, valor líquido, folha e linha de origem. Não foram inventados diagnósticos, notas clínicas, faturas, pagamentos nem resultados.

## Laboratório (mapeamento vs catálogo V1)

Não se aceitam mapeamentos ambíguos automaticamente.

| Métrica | Valor |
| --- | --- |
| Eventos laboratoriais | 137 |
| Descrições únicas | 41 |
| ALINHADO (descrições / eventos) | 1 / 6 |
| POSSIVEL | 12 / 19 |
| AMBIGUO | 2 / 13 |
| SEM_CORRESPONDENCIA | 26 / 99 |
| REVISAR | 0 / 0 |

## Medicamentos e materiais (VENDAS / VENDAS MEDICA)

Não é stock físico actual. `quantidade_inicial` está vazia em todos os candidatos.

| Métrica | Valor |
| --- | --- |
| Descrições únicas | 55 |
| MEDICAMENTO | 52 |
| MATERIAL_CLINICO | 0 |
| PROCEDIMENTO misturado em vendas | 2 |
| OUTRO | 1 |
| Grupos ortográficos para confirmação de enfermagem | 32 (62 linhas) |

Variantes de grafia (incluindo possíveis formas de Ceftriaxona) ficam só como sugestão de revisão. Sem conversão automática para um nome canónico.

## Médicos

3 nomes extraídos da actividade histórica. Nenhum utilizador `MEDICO` foi criado. O mapeamento contra a BD fica no dry-run (ver `MIGRACAO_HISTORICA_DRY_RUN.md`).

## Qualidade de datas

Datas suspeitas **não** foram corrigidas.

| Métrica | Valor |
| --- | --- |
| Data válida mais antiga | 1978-08-05 |
| Data válida mais recente | 2026-08-28 |
| Ano dominante | 2026 |
| Datas malformadas | 1 |
| Datas suspeitas | 5 |
| Fora do período dominante (±1 ano) | 1 |

## Financeiro

| Métrica | Valor |
| --- | --- |
| Registos financeiros de linha (preço e/ou líquido) | 566 |
| Fórmulas na pasta | 636 |
| Erros Excel (`#REF!`, …) | 5 |

Totais da folha `SOMA GERAL` e outras linhas de resumo **não** entram como transações de paciente. Não foram criadas faturas SGCS.

## Revisão manual e rejeições

| Métrica | Valor |
| --- | --- |
| Itens em `migracao_revisao_manual.csv` | 739 |
| Sem paciente identificável | 265 |
| Descrição insuficiente | 93 |
| Erro Excel | 4 |
| Data suspeita | 5 |
| Exame não alinhado | 131 |
| Ecografia a rever | 58 |
| Cirurgia a rever | 60 |
| Consulta ambígua | 19 |
| Medicamento ambíguo | 98 |
| Item excluído do stock automático | 4 |
| Preço inconsistente | 2 |

CSVs gerados (pasta privada, fora do Git): `pacientes_migracao_sauvida.csv`, `historico_clinico_sauvida.csv`, `historico_financeiro_sauvida.csv`, `stock_referencia_sauvida.csv`, `duplicados_pacientes.csv`, `mapeamento_consultas.csv`, `mapeamento_exames_historicos.csv`, `medicamentos_revisao.csv`, `medicos_historicos.csv`, `migracao_revisao_manual.csv`.
