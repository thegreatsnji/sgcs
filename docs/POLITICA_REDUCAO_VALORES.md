# Política de redução de valores (receção)

## Princípio

- **Preço oficial:** `Servico.preco` no catálogo (após confirmação clínica).
- **Preço cobrado:** snapshot em `ItemFatura.preco` por linha de fatura.

A redução na receção **não altera** o catálogo nem faturas já emitidas.

## Configuração (`ConfiguracaoFaturacao`)

| Campo | Predefinição |
|---|---|
| `permitir_reducao_rececao` | true |
| `limite_reducao_rececao_percentual` | null (clínica define) |
| `exigir_motivo_reducao` | true |
| `exigir_autorizacao_acima_limite` | true |
| `permitir_valor_zero` | false |
| `mostrar_reducao_no_recibo` | false |

## Motivos (enum `MotivoReducao`)

Lista inicial conforme especificação Sprint 18.1; «Outro» exige observação.

## Interface

Preferir **«Redução do valor»** ou **«Valor especial autorizado»** — evitar linguagem estigmatizante.

## Auditoria

Eventos: `REDUCAO_VALOR_*`, `TENTATIVA_ALTERAR_PRECO_OFICIAL`.

Ver também: `docs/FLUXO_PRECO_FLEXIVEL_RECECAO.md`, `docs/AUTORIZACAO_REDUCOES.md`.
