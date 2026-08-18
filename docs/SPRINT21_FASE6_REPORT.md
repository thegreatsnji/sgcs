# Sprint 21 Fase 6 — Relatório

**Data:** 2026-08-18  
**Apply / importação / alteração V1:** não executados  
**Estado:** `AGUARDA_VALIDACAO_STOCK_E_PRECOS`

Estatísticas preenchidas após geração do pacote (comando `generate_sauvida_current_pack`).

| Métrica | Valor |
| --- | ---: |
| Itens extraídos das fotos | 23 |
| Medicamentos | 8 |
| Materiais clínicos | 8 |
| Testes rápidos | 5 |
| Documentos/cartões | 2 |
| Novos itens (só na foto) | 12 |
| Já conhecidos (match exacto) | 1 |
| Possíveis duplicados | 7 |
| Grafias divergentes / só histórico | 43 |
| Não-stock (cartões/procedimentos) | 5 |
| Preços divergentes (ambos preenchidos) | 0 |
| Novos serviços | 6 |
| Serviços iguais (preço foto = V1) | 0 |
| Preços a rever (foto sem valor numérico) | 13 |
| Itens a aguardar enfermeira | 21 (stock, sem cartões) |
| Preços a aguardar Direcção | 19 linhas do preçário foto + V1 clínicos ausentes na foto |
| Preços da foto assumidos automaticamente | 0 |
| Versão V1_1 gerada | 0 |

Detalhe de reconciliação e preços: ver output do comando e pasta privada gitignored.

Pendências: enfermeira (quantidades e `manter_no_stock`); Direcção (preços e novos serviços).
