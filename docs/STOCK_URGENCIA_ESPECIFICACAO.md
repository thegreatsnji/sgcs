# Especificação — Stock de Urgência (sem farmácia comercial)

A enfermeira usa só:

**Stock de Urgência → Entrada / Saída / Histórico**

## Ecrã principal

| Campo | Uso |
| --- | --- |
| Nome | Item confirmado |
| Quantidade actual | Calculada pelos movimentos — **não editável** |
| Stock mínimo | Limiar de alerta |
| Estado | DISPONIVEL / STOCK_BAIXO / SEM_STOCK |
| Validade (opcional) | PROXIMO_VALIDADE / EXPIRADO |

## Acções

- **Entrada** — cria movimento ENTRADA
- **Saída** — cria movimento SAIDA

## Movimentos

Tipos: `ENTRADA`, `SAIDA`, `AJUSTE`, `PERDA_VALIDADE`

Cada movimento guarda: item, quantidade, tipo, data, utilizador, observação opcional. Paciente/consulta opcional.

## Fora de âmbito

Fornecedor, compras, margem, POS, lote obrigatório, warehouse, código de barras, novos perfis, farmácia comercial.

A quantidade actual **nunca** é editada directamente (o modelo actual `MedicamentoUrgencia.quantidade_stock` não deve ser o caminho da UI futura).
