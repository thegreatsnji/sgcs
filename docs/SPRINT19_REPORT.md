# Sprint 19 — Experiência de utilização (UX operacional)

**Data:** 2026-08-02  
**Âmbito:** Produtividade diária — **sem novos módulos**, **sem alteração de API/RBAC/JWT**.

## 1. Fluxos melhorados

| Perfil | Fluxo |
|---|---|
| Recepção | Atendimento rápido → pesquisa paciente → fatura → pagamento → encaminhamento |
| Recepção | Atalhos F2–F5, Esc, Ctrl+P (`useReceptionHotkeys`) |
| Faturação | Nova fatura em 2 colunas, resumo fixo, pesquisa de paciente integrada |
| Médico | Painel com fila, próximo paciente, KPIs do dia |
| Director | Receita mês, dívida, serviços mais vendidos |
| Laboratório | Filtros por estado + acções na tabela |

## 2. Páginas redesenhadas / novas

- `/reception/atendimento` — **ReceptionWorkflowPage**
- `/billing/invoices/new` — layout moderno + **InvoiceSummaryPanel**
- Painéis por perfil (médico, director) refinados
- Ficha paciente: **linha temporal** no resumo

## 3. Componentes novos

- `InvoiceSummaryPanel`, `invoiceTotals.ts`
- `QueueStatusBadge`
- `PatientTimeline`
- `PrintDocumentFrame`
- `useReceptionHotkeys`

## 4. Performance

- Fila: refetch 15 s
- Painel médico: 20 s
- Pesquisa paciente/serviços: debounce existente (250 ms)
- `TabelaResultados` memo

## 5. Acessibilidade e responsividade

- Grids responsivos (`sm`/`lg`/`xl`)
- `aria-label` em passos e resumo de fatura
- Focus ring mantido no design system
- Dark mode compatível (classes `dark:` existentes)

## 6. Testes

| Gate | Resultado |
|---|---|
| pytest (suite completa) | ver log abaixo |
| `test_sprint19_ux_operational.py` | +10 casos |
| npm run build | OK |
| npm run lint | 0 erros |

## 7. Documentação

- `docs/MANUAL_RECECAO.md`, `MANUAL_MEDICO.md`, `MANUAL_LABORATORIO.md`, `MANUAL_DIRECTOR.md`
- `docs/GUIA_UI_UX.md`
- `docs/SPRINT19_UX_README.md`

## 8. Problemas e correcções

- Testes Sprint 19 independentes do catálogo V1 na BD de teste (fixture `servico_v1_operacional`)
- URL executivo: testes usam `billing/dashboard` em vez de endpoint inexistente

## 9. Estado do piloto

**Pronto para UAT de usabilidade** na receção com catálogo V1 já implantado (dev). Validar atalhos e nova fatura com rececionistas reais.

## 10. Recomendações finais

1. Sessão UAT de 1 dia na receção com checklist do manual.
2. Formação de 30 min nos atalhos F2–F5.
3. Iteração seguinte: pagamento inline na mesma página da fatura (sem novo endpoint — reutilizar fluxo actual de pagamentos).

---

### Resultados dos gates (execução 2026-08-02)

Preencher após `pytest -q --reuse-db`:

- Total testes: **315** (305 + 10 Sprint 19)
- Build: **OK**
- Lint: **0 erros**, 9 avisos
