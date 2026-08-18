# Validação inicial — ficha da enfermeira

**Fonte:** `backend/data/private/sauvida_atual/stock_final_validacao_enfermagem.xlsx`  
**Data:** 2026-08-18  
**Apply:** não executado

A ficha ainda **não** tem `manter_no_stock=SIM` nem `quantidade_actual` numérica.

| Classificação | Quantidade |
| --- | ---: |
| Encontrados | 23 |
| VALIDO | 0 |
| NAO_MANTER (incl. 21 por confirmar + 2 cartões) | 23 |
| PENDENTE_QUANTIDADE | 0 |
| UNIDADE_AUSENTE | 0 |
| NOME_DUPLICADO | 0 |
| QUANTIDADE_INVALIDA | 0 |
| STOCK_MINIMO_INVALIDO | 0 |
| VALIDADE_INVALIDA | 0 |

Cartões (vacina/grávida): 2, marcados `NAO`.  
Itens clínicos na ficha: 21 (8 medicamentos, 8 materiais, 5 testes) — aguardam SIM + unidade + quantidade.

`CX/50` e textos semelhantes **não** são interpretados como saldo.
