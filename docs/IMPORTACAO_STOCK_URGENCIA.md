# Importação do stock de urgência

Fonte: ficha da enfermeira `stock_final_validacao_enfermagem.xlsx` (pasta privada).

```bash
python manage.py import_stock_urgencia --dry-run
python manage.py import_stock_urgencia --apply --actor-email enfermeira@sauvida.gw
```

## Regras

- Só linhas `manter_no_stock = SIM`.
- Quantidade só se for número inteiro (ex.: `8`). `CX/50` **não** é importado como 50.
- Não duplica itens com o mesmo nome.
- Quantidade inicial cria movimento `ENTRADA` / origem `IMPORTACAO`.
- Idempotente: segunda execução ignora os já existentes.
