# UAT presencial — Médico

**Painel:** `/dashboard/doctor`  
**Referência:** [MANUAL_MEDICO.md](MANUAL_MEDICO.md), [FORMACAO_MEDICO.md](FORMACAO_MEDICO.md)

## Tempos-alvo

| Actividade | Meta | Medido (s) | Desvio |
|------------|-----:|----------:|--------|
| Abertura PCE / consulta (rede estável) | ≤ 3 s | | |
| Abrir paciente a partir da fila | — | | |

---

## Casos de teste

| ID | Objectivo | Cenário | Passos resumidos | Resultado esperado | Obtido | Estado | Grav. | Resp. | Evidência |
|----|-----------|---------|------------------|-------------------|--------|--------|-------|-------|-----------|
| M01 | Login | Médico activo | Entrar no piloto | Painel médico | | | | | |
| M02 | Fila | Manhã típica | Abrir fila de consultas | Lista espera + próximo paciente | | | | | |
| M03 | Abrir paciente | Da fila | Seleccionar utente | Ficha com tabs (resumo, histórico) | | | | | |
| M04 | Histórico | Antecedentes | Separador histórico / clínico | Dados anteriores visíveis | | | | | |
| M05 | Iniciar consulta | Consulta do dia | Abrir consulta agendada | Estado em curso | | | | | |
| M06 | Sinais vitais | Registo | Preencher PA, FC, etc. | Gravado no episódio | | | | | |
| M07 | SOAP | Nota clínica | Subjective/Objective/Assessment/Plan | Persistência sem perda | | | | | |
| M08 | Diagnóstico | CID/descrição | Adicionar diagnóstico | Listado na consulta | | | | | |
| M09 | Pedido exame | Laboratório | Solicitar exame alinhado V1 | Pedido no lab. | | | | | |
| M10 | Resultado anterior | Histórico lab. | Ver resultado publicado | Acesso leitura | | | | | |
| M11 | Concluir | Fim consulta | Concluir / alta da consulta | Estado concluído; fila actualizada | | | | | |
| M12 | Seguimento | Retorno | Agendar nova consulta | Marcação criada | | | | | |
| M13 | Impressão | Se aplicável | Resumo/receita impressão | Layout legível; logótipo/rodapé | | | | | |

---

## Resumo da sessão

| Métrica | Valor |
|---------|------:|
| Casos executados | /13 |
| Aprovados | |
| Falhados | |
| Bloqueados | |

**Médico:** __________________ **Data:** __________ **Facilitador:** __________________
