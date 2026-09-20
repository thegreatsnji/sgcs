# UAT presencial — 5 fluxos operacionais SauVida

**Objectivo:** ver se a pessoa completa a tarefa **sem ajuda** e sem perceber a arquitectura do SGCS.  
Não é um questionário. Uma linha por tentativa.

**Resultado:** `PASSOU` | `PASSOU COM DIFICULDADE` | `FALHOU`

Registar também: **Tempo**, **Problema observado**, **Comentário do utilizador**, **Acção necessária**.

Se o ecrã «pensa» por rede/servidor, marcar *lento (backend/rede)* — não misturar com UX.

---

## Como observar

1. Dar a tarefa em linguagem da clínica (coluna «Tarefa»).
2. Não apontar botões. Só intervir se a pessoa parar > 1 minuto ou pedir ajuda (aí: `PASSOU COM DIFICULDADE` ou `FALHOU`).
3. Cronómetro do início da tarefa até o resultado visível (recibo impresso, consulta aberta, stock actualizado, etc.).

---

## Receção

| ID | Tarefa | Meta | Resultado | Tempo | Problema | Comentário | Acção |
|----|--------|------|-----------|-------|----------|------------|-------|
| R1 | Encontrar um utente pelo nome ou telefone | ≤ 15 s | | | | | |
| R2 | Atendimento normal: utente conhecido, 1 serviço, pagar tudo, recibo, encaminhar ao médico | ≤ 2 min | | | | | |
| R3 | Acrescentar um serviço à fatura | ≤ 15 s | | | | | |
| R4 | Aplicar redução autorizada (motivo) **sem** confundir com pagamento parcial | — | | | | | |
| R5 | Registar pagamento integral | ≤ 30 s | | | | | |
| R6 | Emitir / imprimir recibo | ≤ 30 s | | | | | |
| R7 | Completar pagamento quando a fatura ficou a meio | — | | | | | |

Utente: ____________  Data: ____________  Observador: ____________

---

## Médico

| ID | Tarefa | Meta | Resultado | Tempo | Problema | Comentário | Acção |
|----|--------|------|-----------|-------|----------|------------|-------|
| M1 | Identificar o próximo utente e abri-lo (Atender agora) | ≤ 15 s | | | | | |
| M2 | Ver motivo/queixa e se há histórico **anterior** vs consulta SGCS | — | | | | | |
| M3 | Preencher dados clínicos mínimos e concluir | — | | | | | |
| M4 | Pedir laboratório quando necessário | — | | | | | |

Médico: ____________  Data: ____________  Observador: ____________

---

## Laboratório

| ID | Tarefa | Meta | Resultado | Tempo | Problema | Comentário | Acção |
|----|--------|------|-----------|-------|----------|------------|-------|
| L1 | Encontrar o pedido certo (paciente + exame) | ≤ 15 s | | | | | |
| L2 | Ver o médico solicitante (se existir) | — | | | | | |
| L3 | Processar e introduzir resultado (rascunho ≠ validado) | — | | | | | |
| L4 | Validar (deve pedir confirmação) e consultar/imprimir | — | | | | | |

Técnico: ____________  Data: ____________  Observador: ____________

---

## Stock de urgência (enfermagem)

| ID | Tarefa | Meta | Resultado | Tempo | Problema | Comentário | Acção |
|----|--------|------|-----------|-------|----------|------------|-------|
| S1 | Encontrar o item pelo nome | — | | | | | |
| S2 | Entrada com quantidade | ≤ 30 s | | | | | |
| S3 | Saída com quantidade | ≤ 30 s | | | | | |
| S4 | Confirmar que a quantidade da tabela **não** se edita à mão | — | | | | | |
| S5 | Tentar saída maior que o stock — deve recusar | — | | | | | |
| S6 | Abrir histórico do movimento | — | | | | | |

Enfermeira: ____________  Data: ____________  Observador: ____________

Estados esperados na lista: **Normal** / **Stock baixo** / **Sem stock**.

---

## Direção (preferir telemóvel)

| ID | Tarefa | Meta | Resultado | Tempo | Problema | Comentário | Acção |
|----|--------|------|-----------|-------|----------|------------|-------|
| D1 | Ver receita de hoje e do mês | — | | | | | |
| D2 | Ver pagamentos de hoje e dívida/saldo pendente | — | | | | | |
| D3 | Ver utentes atendidos, consultas e laboratório | — | | | | | |
| D4 | Ver serviços mais utilizados | — | | | | | |
| D5 | Ver stock baixo / sem stock (se o cartão aparecer) | — | | | | | |

Director: ____________  Data: ____________  Observador: ____________  Telemóvel: sim / não

Não pedir interpretação de gráficos extra. O teste passa se os números do dia/mês forem encontrados sem ajuda.

---

## Notas de sessão

Lento por rede/servidor (não UX):

-

Impedimentos de dados (médico em consulta, stock ainda por validar pela enfermagem, etc.):

-
