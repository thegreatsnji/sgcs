# Stock de urgência

Módulo simples para medicamentos e materiais de uso clínico. **Não é farmácia comercial.**

Reutiliza os modelos `MedicamentoUrgencia` e `MovimentoStockUrgencia` (`apps.pharmacy`).

## Regras

- A quantidade actual **não** se edita na ficha.
- Toda alteração cria um movimento: `ENTRADA`, `SAIDA`, `AJUSTE`, `PERDA_EXPIRACAO`.
- Stock nunca fica negativo.
- Movimentos são imutáveis.
- O texto das fotografias (`CX/50`) fica em `quantidade_texto_original`; o saldo físico só entra por movimento confirmado.

## Perfis

| Perfil | Acesso |
| --- | --- |
| ENFERMEIRO | ver, criar item, entrada, saída, ajuste, histórico |
| DIRECTOR | ver e histórico |
| MEDICO | ver (sem alterar) |
| RECECIONISTA | sem acesso de alteração |
| ADMINISTRADOR | total |

Permissões: `stock.*` e, por compatibilidade, `pharmacy.view/create/edit`.

## API

- `GET/POST /api/v1/stock/items/`
- `POST /api/v1/stock/items/{id}/entrada|saida|ajuste|perda/`
- `GET /api/v1/stock/movements/`
- `GET /api/v1/stock/dashboard/`

Os caminhos `/api/v1/pharmacy/urgent-medicines/` mantêm-se.

## UI

- `/stock` — lista, filtros, novo item, entrada/saída
- `/stock/historico` — movimentos

## Importação

```bash
python manage.py import_stock_urgencia --dry-run
python manage.py import_stock_urgencia --apply --actor-email EMAIL
```

Só importa linhas com `manter_no_stock=SIM`. Não converte `CX/50` em 50 unidades.
