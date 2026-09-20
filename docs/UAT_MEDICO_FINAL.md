# UAT final — perfil MÉDICO

**Pré-requisitos:** migrations aplicadas; `seed_rbac`; 2 médicos (A/B); 1 rececionista;
1 técnico de laboratório; 2 pacientes fictícios; serviço LABORATORIO no catálogo.

**Gates automatizados (2026-08-23):** 484 passed · 2 skipped · 0 failed · build OK · lint 0 errors.

Marcar: **PASSOU** / **COM DIFICULDADE** / **FALHOU**.

---

## 1. Fila exclusiva

Receção atribui paciente ao Dr. A. Confirmar na fila do Dr. A. Dr. B **não** vê.
Paciente sem médico: **não** aparece em A nem B; permanece na Receção “Por atribuir”.

| Resultado | Observação |
|---|---|
| | |

## 2. Fluxo Receção → médico

Check-in → pagamento (fluxo existente) → atribui Dr. A → Dr. A “Atender agora”.
Confirmar mesmo paciente / check-in / consulta; médico correcto; sem duplicados.

| Resultado | Observação |
|---|---|
| | |

## 3. Privacidade financeira

Sem “Faturação” no cabeçalho nem “Pagamentos” na ficha. Abrir `/billing/invoices` →
acesso negado. Prontuário mostra só estado operacional (Sem fatura / Pendente / Parcial / Pago)
**sem montantes**.

| Resultado | Observação |
|---|---|
| | |

## 4. Triagem

Com vitais no check-in: cartão “Sinais vitais da triagem” com data/origem.
“Usar como base” preenche formulário **sem** alterar o registo original da triagem.

| Resultado | Observação |
|---|---|
| | |

## 5. Autosave SOAP

Escrever S/O/A/P; aguardar >1,5 s; recarregar — dados persistem.
Confirmar: não cria 2.ª consulta; não conclui; não cria lab/fatura/prescrição.

| Resultado | Observação |
|---|---|
| | |

## 6. Diagnóstico e prescrição

Adicionar Diagnóstico/CID. Tab Prescrição: medicamento sem pedir ID da consulta.
Confirmar ligação à consulta; stock **não** movimenta; faturação **não** criada.

| Resultado | Observação |
|---|---|
| | |

## 7. Lab → Receção

Pedir exame do catálogo. Pedido clínico criado; **sem** fatura automática.
Receção vê em pedidos pendentes; factura pelo catálogo; marca regularizado.
Confirmar que reabrir o mesmo pedido não gera cobrança automática duplicada.

| Resultado | Observação |
|---|---|
| | |

## 8. Resultado não validado / validado

Lab introduz resultado sem validar → médico vê “Aguarda validação” **sem valores**.
Após validar → valores visíveis no prontuário.

| Resultado | Observação |
|---|---|
| | |

## 9. Seguimento

“Recomendar seguimento” — texto deve deixar claro que **não** cria marcação.
Confirmar que nenhuma consulta nova aparece na agenda/Receção.

| Resultado | Observação |
|---|---|
| | |

## 10. Conclusão idempotente

Concluir consulta. Fila/consulta em estado final. Segundo “Concluir” sem duplicar efeitos.
Receção percebe atendimento terminado.

| Resultado | Observação |
|---|---|
| | |

## 11. Paciente importado

Histórico anterior identificado e read-only. Nova consulta SGCS editável;
não altera PatientHistory migrado.

| Resultado | Observação |
|---|---|
| | |

## 12. Percurso UX (bloqueantes apenas)

Painel → próximo → Atender → triagem → SOAP → Dx → Rx → lab → concluir.
Anotar só bloqueantes de piloto.

| Resultado | Observação |
|---|---|
| | |

---

## Critério de aprovação

Bloqueia piloto se: valores lab não validados expostos; montantes financeiros ao médico;
paciente de outro médico na fila; duplicação de consulta/check-in na atribuição.
