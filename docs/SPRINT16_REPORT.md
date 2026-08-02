# Relatório Sprint 16 — Catálogo SauVida

**Data:** 2026-07-31

## 1. Resumo executivo

Catálogo central alargado (`Servico` + departamentos + especialidades + laboratório), importação segura com preços pendentes, pesquisa na faturação da Receção, histórico de preços e **271** testes backend verdes.

## 2. Auditoria inicial

`docs/SPRINT16_CATALOGO_AUDIT.md`

## 3–4. Modelos

**Reutilizados:** `Servico`, `Departamento`, `EspecialidadeMedica`, `TipoExameLaboratorio`, `PerfilClinica`, `ItemFatura`.

**Novos/alterados:** `ServicoPrecoHistorico`, `MedicoPerfil`; campos operacionais em `Servico`, dept/esp, tipos lab, perfil clínica.

## 5. Migrations

- `billing.0002_sprint16_catalogo`
- `clinic_settings.0003_sprint16_catalogo`
- `audit_logs.0011_sprint16_catalogo`

## 6. Categorias

13 categorias SauVida + legado (`EXAME`, `OUTRO`, `INTERNAMENTO`).

## 7. Departamentos

10 departamentos em `backend/data/departamentos_sauvida.json`.

## 8. Especialidades

4 em `especialidades_sauvida.csv`.

## 9. Serviços preparados

**36** linhas em `catalogo_servicos_sauvida.csv` (consultas, eco, enfermagem, cirurgia/maternidade catálogo, laboratório, documentos, imunização).

## 10. Exames laboratoriais

**9** tipos em `exames_laboratoriais_sauvida.csv`.

## 11–12. Preços

- **Confirmados:** 0 (política Sprint 16 — não inventar).
- **Pendentes:** **36** (`REVISAR_COM_CLINICA`).

## 13. Comando

`import_catalogo_sauvida` (`--dry-run` / `--apply` / `--update-existing`).

## 14–15. Importação

| Modo | Criados | Pendentes |
|------|--------:|----------:|
| dry-run | 0 | 36 |
| apply | 0 | 36 |

Dept/esp sincronizados no `--apply`; exames lab gravados quando aplicável.

## 16. Receção

`ServiceSearchPicker`, API `operacional=1`, menu faturação existente.

## 17. Permissões

- Admin: total catálogo + preço
- Director: ver + relatórios (existente)
- Receção: ver/usar serviços, sem alterar preço
- Médico: `billing.view` (pesquisa clínica)
- Laboratório: sem billing de preços

## 18. Histórico de preços

`ServicoPrecoHistorico` + endpoint `price-history`.

## 19. Ficheiros principais

`backend/apps/billing/*`, `backend/apps/settings/models.py`, `backend/data/*`, `frontend/src/features/billing/components/ServiceSearchPicker.tsx`, `InvoiceCreatePage.tsx`, docs Sprint 16.

## 20–22. Testes / build / lint

- **271** pytest passed
- `npm run build` OK
- `npm run lint` 0 erros

## 23. Riscos

- Preços a zero até validação clínica
- `TipoConsulta.preco_base` ainda no modelo (documentar descontinuação)
- UI admin médico pendente

## 24. Decisões pendentes

- Confirmar preço FCFA por linha do CSV
- Política de descontos na receção

## 25. Sprint 17

Importar preços confirmados com `--apply --update-existing`; UI `MedicoPerfil`; filtros avançados na lista admin de serviços; ligação automática pedido lab → serviço.
