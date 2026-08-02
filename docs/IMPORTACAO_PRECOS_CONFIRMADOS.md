# Importação de preços confirmados

## Ficheiro

`backend/data/precos_validacao_clinica.csv`

Colunas: `codigo`, `nome`, `categoria`, `departamento`, `preco_actual_fcfa`, `preco_confirmado_fcfa`, `confirmado_por`, `data_confirmacao`, `observacoes`.

## Comandos

```bash
python manage.py import_catalogo_sauvida \
  --file backend/data/precos_validacao_clinica.csv \
  --dry-run

python manage.py import_catalogo_sauvida \
  --file backend/data/precos_validacao_clinica.csv \
  --apply \
  --update-existing \
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
