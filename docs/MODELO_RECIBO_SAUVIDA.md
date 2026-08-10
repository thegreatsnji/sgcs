# Modelo de recibo SauVida

## Referência

Alinhado ao livro de recibos em papel: logótipo, identificação da clínica, número do recibo, texto «Recebi do/a senhor/a», «A importância de», «Referente a», data e assinatura do caixa.

## Implementação

- API: `GET /api/v1/billing/receipts/{id}/impressao/` (`?segunda_via=1` para segunda via, **mesmo número**).
- UI: `SauVidaReceiptDocument` + `SauVidaReceiptPrint` + `src/styles/print.css` (emblema, logótipo, campos do livro de recibos).
- Imagens por defeito: `frontend/public/branding/` (substituíveis por logótipo no perfil da clínica).

## Configuração (`ConfiguracaoFaturacao`)

- `mostrar_preco_oficial_recibo`
- `mostrar_reducao_recibo` / `mostrar_reducao_no_recibo`
- `mostrar_saldo_recibo`
- `mostrar_ministerio_saude_recibo` (**activo por defeito**, como no livro de recibos em papel)
- `mostrar_valor_por_extenso`
- `formato_recibo` (A4, A5, TERMICO_80)
- `texto_rodape_recibo`

Não são injectados NIF, morada ou contactos inventados — vêm de `PerfilClinica` quando configurados.

## Separação financeira

| Conceito | Origem |
|---|---|
| Preço oficial | `ItemFatura.preco_oficial` |
| Preço cobrado | `ItemFatura.preco` |
| Valor pago | `Pagamento.valor` (acumulado confirmado) |
| Saldo | `Fatura.total` − total pago |
| Redução | `ItemFatura.valor_reducao` (≠ pagamento parcial) |

## Numeração

Formato existente: `REC-{ano}-{sequência}` via `BillingNumberService.generate_receipt()`.
