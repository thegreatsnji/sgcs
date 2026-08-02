# Importação do catálogo SauVida

## Comandos

```bash
cd backend
python manage.py import_catalogo_sauvida --dry-run
python manage.py import_catalogo_sauvida --apply
python manage.py import_catalogo_sauvida --apply --update-existing
```

## Opções

| Opção | Descrição |
|--------|-----------|
| `--file` | CSV de serviços |
| `--skip-invalid` | Ignora linhas inválidas |
| `--create-missing-relations` | Cria dept/esp referenciados (legado) |
| `--report-path` | JSON com resumo |

## Preços

- Coluna `preco_fcfa`: valor inteiro em FCFA ou `REVISAR_COM_CLINICA` / vazio.
- Linhas pendentes **não** são gravadas em `--apply`.

## Resultado típico (Jul 2026)

- **36** linhas de serviço preparadas, **0** importadas (preços por confirmar).
- Departamentos (**10**) e especialidades (**4**) sincronizados ao correr o comando.
- **9** tipos de exame laboratorial ligados quando existir `servico_codigo` correspondente.

## Comando legado

`import_servico_catalog` mantido para CSV antigo; preferir `import_catalogo_sauvida`.
