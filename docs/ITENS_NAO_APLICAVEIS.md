# Itens não aplicáveis — Clínica SauVida (sem internamento)

A clínica **não possui** internamento, gestão de camas ou quartos.

## Locais identificados no SGCS

| Local | Tipo | Acção nesta etapa |
|-------|------|-------------------|
| `apps/billing/constants.py` | Categoria `INTERNAMENTO` em `SERVICE_CATEGORIES` | Mantida no modelo (compatibilidade); excluída da UI/import SauVida |
| `apps/billing/clinic_scope.py` | `EXCLUDED_SERVICE_CATEGORIES`, `EXCLUDED_DEPARTMENT_CODES` | Fonte única para exclusão |
| `data/clinic/catalogo_servicos_sauvida.csv` | Linhas `INT-DIA-*` | `activo=0`; **não importadas** (`import_servico_catalog`) |
| `data/clinic/departamentos_sauvida.json` | Departamento `INT` | `activo: false` |
| `docs/SPRINT15/*`, `AUDITORIA_SPRINT15.md` | Documentação roadmap v1.9 | Referência apenas |
| `ServicoViewSet.get_queryset` | API listagem serviços | Exclui `INTERNAMENTO` por defeito (`?include_excluded=1` para admin técnico) |

## Termos pesquisados

`INTERNAMENTO`, `internamento`, `cama`, `quarto`, `ward`, `admission`, `inpatient` — sem módulo de camas implementado; apenas categoria de catálogo e dados de referência.

## O que não foi feito

- Nenhuma migration destrutiva.
- Nenhuma remoção do enum `INTERNAMENTO` na base de dados.

## Próximo passo

Após importação do preçário real, confirmar que nenhuma linha de diária/cama entra no CSV operacional; usar categorias `CONSULTA`, `EXAME`, `PROCEDIMENTO`, `OUTRO`.
