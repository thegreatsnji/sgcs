# Sprint 22.1 — Inicialização do stock real

**Estado:** `STOCK_REAL_AGUARDA_VALIDACAO`

A ficha da enfermeira existe mas **não está preenchida** (`manter_no_stock` e `quantidade_actual` vazios). O apply foi **bloqueado**. Não se inventaram quantidades. `CX/50` não foi convertido.

## Estatísticas da ficha

| Item | Valor |
| --- | ---: |
| Itens na ficha | 23 |
| Confirmados (`manter=SIM` + quantidade) | 0 |
| Importados | 0 |
| Pendentes / por confirmar | 21 |
| Cartões (não stock) | 2 |
| Quantidades iniciais importadas | 0 |
| Movimentos criados | 0 |
| Duplicados | 0 |
| Validades importadas | 0 |

## Dry-run

Escrita BD: **0**. Log: `docs/logs/stock_urgencia_inicial_dry_run.txt`.

## Backup / apply

Backup de apply: não gerado (sem escrita). Apply: não executado.

## UAT

Guião em `docs/UAT_STOCK_ENFERMAGEM.md`. A executar na clínica depois das quantidades reais.

## Testes / gates

- `manage.py check` OK  
- `makemigrations --check` OK  
- Pharmacy: **23 passed**  
- Suite: **399 passed**, 2 skipped, **2 failed** pré-existentes na Receção  
- Frontend: sem alterações nesta sub-sprint; build/lint da Sprint 22 mantêm-se.

## Pendências

Enfermeira: `manter_no_stock=SIM`, unidade, quantidade inteira.  
Direcção: preços (Fase 6).  
Depois: backup + `--apply --actor-email`.
