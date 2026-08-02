# UAT presencial — Recepção

**Rota rápida:** `/reception/atendimento`  
**Referência:** [MANUAL_RECECAO.md](MANUAL_RECECAO.md), [FORMACAO_RECECAO.md](FORMACAO_RECECAO.md)

## Tempos-alvo (medir na sessão)

| Actividade | Meta | Medido (s) | Desvio | Observações |
|------------|-----:|----------:|--------|-------------|
| Pesquisa de paciente | ≤ 2 s | | | |
| Criação de paciente | — | | | |
| Criação de fatura | — | | | |
| Pagamento | — | | | |
| Emissão de recibo | ≤ 30 s | | | |
| Check-in | — | | | |
| **Atendimento simples (fim-a-fim)** | ≤ 2 min | | | |

---

## Casos de teste

| ID | Objectivo | Cenário | Passos resumidos | Resultado esperado | Obtido | Estado | Grav. | Resp. | Evidência |
|----|-----------|---------|------------------|-------------------|--------|--------|-------|-------|-----------|
| R01 | Login | Rececionista activo | 1. Abrir URL piloto 2. Entrar com credenciais | Sessão iniciada; painel recepção | | | | | |
| R02 | Pesquisa paciente | Utente existente | 1. Atendimento rápido 2. Pesquisar nome/telefone/processo (parcial) | Resultados em ≤2 s; selecção correcta | | | | | |
| R03 | Novo paciente | Utente novo | 1. F2 ou Novo paciente 2. Preencher obrigatórios 3. Guardar | Paciente criado; aparece na pesquisa | | | | | |
| R04 | Marcação | Com consulta | 1. Marcações 2. Nova 3. Associar paciente/médico | Marcação visível na agenda | | | | | |
| R05 | Check-in | Dia da consulta | 1. Triagem/check-in 2. Seleccionar paciente | Entrada na fila | | | | | |
| R06 | Triagem | Classificação | 1. Cor/prioridade 2. Confirmar | Estado na fila actualizado | | | | | |
| R07 | Nova fatura | Serviço V1 | 1. F3 ou Nova fatura 2. Paciente 3. Adicionar serviço | Fatura criada; preço oficial visível | | | | | |
| R08 | Pesquisa serviço | Catálogo | 1. Pesquisar «Consulta», «Glicose», etc. 2. Filtrar categoria | Só serviços operacionais V1 | | | | | |
| R09 | Preço normal | Sem redução | 1. Item com preço oficial = cobrado | Total = catálogo | | | | | |
| R10 | Redução | Desconto autorizado | 1. Activar redução 2. Valor cobrado &lt; oficial | Motivo obrigatório; oficial preservado | | | | | |
| R11 | Motivo redução | Validação | 1. Tentar sem motivo 2. Com motivo «Outro» + obs. | Bloqueio / sucesso conforme regra | | | | | |
| R12 | Pagamento integral | Fatura fechada | 1. Pagar total 2. Confirmar | Estado PAGA; saldo 0 | | | | | |
| R13 | Pagamento parcial | 1.º pagamento | 1. Pagar &lt; total | Estado PARCIAL; saldo correcto (≠ redução) | | | | | |
| R14 | Saldo pendente | Visualização | 1. Ver fatura | Saldo = total cobrado − pago | | | | | |
| R15 | Segundo pagamento | Liquidação | 1. Segundo pagamento até saldo 0 | Fatura PAGA | | | | | |
| R16 | Recibo | Após pagamento | 1. Emitir/ver recibo | Número único; valores correctos | | | | | |
| R17 | Impressão | Recibo | 1. Imprimir (Ctrl+P se aplicável) | Layout legível; sem menus | | | | | |
| R18 | Segunda via | Reimpressão | 1. Segunda via no recibo | Marcado SEGUNDA VIA; auditoria | | | | | |
| R19 | Encaminhar médico | Pós-pagamento | 1. Fila/encaminhamento 2. Médico | Médico vê na fila | | | | | |
| R20 | Histórico | Paciente | 1. Ficha paciente 2. Pagamentos/histórico | Dados consistentes com faturas | | | | | |

---

## Validações específicas Sprint 19

| Item | Como testar | Esperado | Obtido | Estado |
|------|-------------|----------|--------|--------|
| Atalho F2 | Tecla F2 (fora de campo texto) | Abre novo paciente | | |
| Atalho F3 | F3 | Nova fatura | | |
| Atalho F4 | F4 | Pagamentos | | |
| Atalho F5 | F5 | Actualiza fila | | |
| Esc | Esc no atendimento rápido | Limpa selecção paciente | | |
| Mensagens PT | Provocar erro (ex. sem paciente) | Texto claro em português | | |
| Portátil clínico | Mesma rede Wi‑Fi piloto | Layout utilizável; sem scroll excessivo | | |
| Catálogo legado | Pesquisa operacional | Serviços antigos não aparecem | | |
| Sem preço confirmado | Se existir serviço teste | Bloqueio com mensagem | | |
| Permissões | Tentar acção admin | 403 ou ausência de menu | | |

---

## Resumo da sessão

| Métrica | Valor |
|---------|------:|
| Casos executados | /20 |
| Aprovados | |
| Falhados | |
| Bloqueados | |
| Necessita ajuste | |
| Tempo médio atendimento simples | min |

**Facilitador:** __________________ **Data:** __________ **Assinatura recepção:** __________________
