# UAT presencial — Director (incl. telemóvel)

**Painel:** `/dashboard/director`  
**Referência:** [MANUAL_DIRECTOR.md](MANUAL_DIRECTOR.md), [FORMACAO_DIRECTOR.md](FORMACAO_DIRECTOR.md)

Testar **no telemóvel real** da clínica (Chrome/Safari) e, se possível, em tablet.

---

## Casos de teste

| ID | Objectivo | Dispositivo | Passos | Esperado | Obtido | Estado | Grav. | Evidência |
|----|-----------|-------------|--------|----------|--------|--------|-------|-----------|
| D01 | Login | Telemóvel | Entrar | Painel executivo | | | | |
| D02 | Receita dia | Telemóvel | Ver KPI receita hoje | Valor legível; actualização | | | | |
| D03 | Receita mês | Telemóvel | Card receita mês | Valor coerente com faturação | | | | |
| D04 | Pagamentos | Telemóvel | Indicador pagamentos hoje | Número compreensível | | | | |
| D05 | Saldos pendentes | Telemóvel | Faturas pendentes / dívida | Sem jargão técnico | | | | |
| D06 | Reduções | Telemóvel | Relatório ou lista reduções | Acesso conforme RBAC | | | | |
| D07 | Serviços top | Telemóvel | Serviços mais vendidos | Lista legível | | | | |
| D08 | Consultas | Telemóvel | KPI consultas | Hoje / concluídas | | | | |
| D09 | Laboratório | Telemóvel | KPI lab. | Pendentes visíveis | | | | |
| D10 | Relatórios | Telemóvel | Relatório executivo completo | Navegação OK | | | | |
| D11 | Responsividade | Telemóvel | Scroll horizontal mínimo | Sem overflow crítico | | | | |
| D12 | Legibilidade | Telemóvel | Sol/luz clínica | Contraste aceitável | | | | |
| D13 | Velocidade | Telemóvel | Abrir painel 3× | &lt; 5 s percepção utilizador | | | | |

---

## Resumo

| Casos executados | /13 | Aprovados | | Falhados | |
|------------------|----:|-----------|---|----------|---|

**Director:** __________________ **Data:** __________
