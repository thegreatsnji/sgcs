# UAT presencial — Laboratório

**Painel:** `/dashboard/laboratory` · **Resultados:** `/laboratory/results`  
**Referência:** [MANUAL_LABORATORIO.md](MANUAL_LABORATORIO.md), [FORMACAO_LABORATORIO.md](FORMACAO_LABORATORIO.md)

## Tempos-alvo

| Actividade | Meta | Medido (s) | Desvio |
|------------|-----:|----------:|--------|
| Registo de resultado (caso simples) | — | | |
| Pesquisa na fila de resultados | ≤ 2 s | | |

---

## Casos de teste

| ID | Objectivo | Cenário | Passos resumidos | Resultado esperado | Obtido | Estado | Grav. | Resp. | Evidência |
|----|-----------|---------|------------------|-------------------|--------|--------|-------|-------|-----------|
| L01 | Login | Técnico lab. | Entrar no piloto | Painel laboratório | | | | | |
| L02 | Pendentes | Fila inicial | Pedidos pendentes | Lista actualizada | | | | | |
| L03 | Receber pedido | Novo pedido médico | Abrir pedido; confirmar recepção | Estado coerente | | | | | |
| L04 | Autorização | Se exigido | Confirmar autorização | Registo auditável | | | | | |
| L05 | Colheita | Amostra | Registar colheita | Ligado ao pedido | | | | | |
| L06 | Processamento | Início análise | Iniciar processamento | Estado «em processamento» | | | | | |
| L07 | Resultados | Entrada dados | Introduzir parâmetros/valores | Gravado; editável | | | | | |
| L08 | Validar | Controlo qualidade | Validar resultado | Estado validado | | | | | |
| L09 | Publicar | Médico vê | Publicar/entregar | Visível no prontuário | | | | | |
| L10 | Impressão | Entrega papel | Imprimir resultado | Formato legível | | | | | |
| L11 | Prontuário | Médico/paciente | Consultar resultado no paciente | Consistência com lab. | | | | | |

---

## Filtros rápidos (Sprint 19)

| Filtro | Esperado | Obtido | Estado |
|--------|----------|--------|--------|
| Pendentes | Lista filtrada | | |
| Em processamento | Lista filtrada | | |
| Validados | Lista filtrada | | |
| Acções Editar/Validar/Imprimir | Funcionais | | |

---

## Resumo da sessão

| Métrica | Valor |
|---------|------:|
| Casos executados | /11 |
| Aprovados | |

**Técnico:** __________________ **Data:** __________
