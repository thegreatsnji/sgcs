# Sprint 18 — Resultado da importação de preços

## Estado

| Fase | Executado | Resultado |
|------|-----------|-----------|
| Validação (`validate_precos_validacao_clinica`) | Sim | 36 PENDENTE, 0 VÁLIDA |
| Backup | Sim | `backups/pre_sprint18/sgcs_pre_import_catalogo_20260731_1400.sql` |
| Dry-run preços | Sim | Ver `docs/logs/sprint18_catalogo_dry_run.txt` |
| **Apply preços** | **Não** | Nenhuma linha com `preco_confirmado_fcfa` preenchido |
| Materialização catálogo (`--apply`) | Pendente operador | Ver secção abaixo |
| Alinhamento laboratório (`--apply`) | Pendente após materialização | — |

## Dry-run de preços (resumo)

- **Linhas:** 36
- **Confirmados (simulados):** 0
- **Pendentes:** 36
- **Ignorados / inválidos:** 0

**Decisão:** importação real de preços **não executada** — conforme princípio “não importar sem confirmação”.

## Apply de preços (quando a clínica entregar o CSV)

```bash
python manage.py sprint18_backup_db   # ou pg_dump via Docker
python manage.py import_catalogo_sauvida \
  --file backend/data/precos_validacao_clinica.csv \
  --dry-run --update-existing --actor-email admin@sauvida.gw
python manage.py import_catalogo_sauvida \
  --file backend/data/precos_validacao_clinica.csv \
  --apply --update-existing --actor-email admin@sauvida.gw
```

Saída esperada em `docs/logs/sprint18_catalogo_apply.txt` após execução.

## Materialização do catálogo (sem preço)

Comando aprovado para cadastro não faturável até confirmação:

```bash
python manage.py import_catalogo_sauvida \
  --file backend/data/catalogo_servicos_sauvida.csv \
  --apply --materialize-without-price \
  --create-missing-relations --update-existing \
  --actor-email admin@sauvida.gw
```

Dry-run: `docs/logs/sprint18_materialize_dry_run.txt`

## Linhas ignoradas

Todas as 36 linhas do ficheiro de preços foram **ignoradas para apply** por ausência de preço confirmado (comportamento esperado).
