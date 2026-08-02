# Sprint 18.1 — Relatório final (SGCS SauVida)

**Data:** 2026-07-31  
**Âmbito:** validação catálogo real OCR, reduções na receção, importação controlada, alinhamento laboratorial, piloto.

---

## 1. Catálogo real analisado

| Métrica | Valor |
|---|---:|
| Serviços no CSV real | **133** |
| Preços claramente confirmados (`preco_confirmado=TRUE`) | **121** |
| Pendentes `REVISAR_COM_CLINICA` | **12** |
| Grupos de duplicados/conflitos | **6** |
| Exames laboratoriais (CSV real) | **97** |

Fonte exclusiva: 7 fotografias (ver `docs/OCR_ANALISE_IMAGENS.md`).

## 2. Itens pendentes e validação

- Gerado `backend/data/catalogo_real_validacao_clinica.csv` (**21 linhas** — 12 pendentes + códigos em conflito).
- Ficha clínica: `docs/FICHA_VALIDACAO_CATALOGO_REAL.md`.
- Resolução de duplicados (sem auto-merge): `docs/RESOLUCAO_DUPLICADOS_CATALOGO_REAL.md`.

## 3. Importação catálogo

- Dry-run final: `docs/logs/catalogo_real_dry_run_final.txt` (121 criados, 12 pendentes).
- **Apply não executado** — aguarda `preco_confirmado_fcfa` na validação clínica.
- `docs/IMPORTACAO_FINAL_CATALOGO_REAL.md`.

## 4. Modelo de preços na fatura

| Conceito | Implementação |
|---|---|
| Preço oficial | `ItemFatura.preco_oficial` (+ catálogo `Servico.preco` inalterado) |
| Preço cobrado (snapshot) | `ItemFatura.preco` (compatível com API existente) |
| Redução | `valor_reducao`, `percentual_reducao`, motivo, observação, origem |
| Autorização | `ReducaoValorAutorizacao` + estados em `ItemFatura.estado_autorizacao_reducao` |

Migration: `billing.0004_sprint18_1_reducao_catalogo` (+ meta `0005`).

## 5. Configuração clínica

`ConfiguracaoFaturacao`: limites de redução, motivo obrigatório, autorização acima do limite, `mostrar_reducao_no_recibo` (predefinição: ocultar no documento ao paciente).

Migration: `clinic_settings.0004_sprint18_1_reducao_faturacao`.

## 6. API e frontend

- `POST/GET /api/v1/billing/reducoes/` — solicitar e listar.
- `POST .../aprovar/`, `.../rejeitar/` — Director/Administrador.
- `GET /api/v1/billing/reports/reducoes/` — indicadores.
- UI: redução em `ServiceSearchPicker`, página `/billing/reducoes/pendentes`.

## 7. Laboratório

- `align_lab_services --file backend/data/exames_laboratoriais_reais.csv`.
- Log dry-run: `docs/logs/lab_real_alignment_dry_run.txt`.
- **Apply** documentado em `docs/ALINHAMENTO_LABORATORIO_REAL.md` (não executado nesta entrega se BD sem tipos pré-carregados).

## 8. Auditoria

Novas ações: `REDUCAO_VALOR_*`, `TENTATIVA_ALTERAR_PRECO_OFICIAL`, `CATALOGO_REAL_IMPORTADO`, `CONFLITO_CATALOGO_RESOLVIDO` (`audit_logs.0012_sprint18_1_meta`).

## 9. Testes e gates

| Gate | Resultado |
|---|---|
| `manage.py check` | OK |
| `makemigrations --check` | OK (após `0012` / `0005` meta) |
| `pytest -q --reuse-db` | **300 passed** |
| `npm run build` | OK |
| `npm run lint` | OK (0 erros; avisos pré-existentes) |

Testes novos: `apps/billing/tests/test_sprint18_1_reductions.py` (11).

## 10. Riscos e decisões pendentes

1. Preencher validação clínica dos **12** pendentes e **6** conflitos antes do apply.
2. Definir `limite_reducao_rececao_percentual` na clínica (campo vazio = sem bloqueio percentual automático).
3. Recibo PDF: configurar `mostrar_reducao_no_recibo` na impressão (armazenamento administrativo já completo).
4. Fluxo frontend para pedir autorização antes de submeter fatura acima do limite (API pronta; UI pode ligar `autorizacaoReducaoId`).

## 11. Estado do piloto

**APROVADO COM RESSALVAS** — funcionalidade de redução e validação de catálogo prontas para UAT; operação com preços reais depende da assinatura da ficha de validação e apply controlado.

---

### Resumo executivo

| Indicador | Valor |
|---|---:|
| Serviços catálogo real | 133 |
| Preços confirmados (CSV) | 121 |
| Preços pendentes | 12 |
| Conflitos resolvidos automaticamente | **0** |
| Serviços importados (apply) | **0** (dry-run apenas) |
| Exames alinhados (apply) | pendente clínica/BD |
| Testes aprovados | 300 |
| Build frontend | Sucesso |
| Lint frontend | Sem erros |
