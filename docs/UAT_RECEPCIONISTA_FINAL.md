# UAT Presencial — Rececionista (SauVida)

**Perfil:** RECECIONISTA  
**Duração alvo:** 45–60 min  
**Pré-requisitos:** 1 médico activo no sistema; catálogo com serviço ~10.000 FCFA; caixa do dia; browser no portátil da Receção.

Marcar: **PASSOU** / **COM DIFICULDADE** / **FALHOU** · Observação livre.

---

## 1. Arranque e navegação

Abrir sessão Receção. Confirmar menu: Painel, Atendimento rápido, Fila, Faturação, Pacientes, Marcações. Confirmar ausência de Financeiro / Stock / Lab / Admin.

| Resultado | Observação |
|---|---|
| | |

---

## 2. Walk-in novo

Atendimento rápido → pesquisar nome fictício inexistente → registar → triagem → fatura 10.000 → pagar 10.000 → recibo → atribuir médico. Confirmar 1 utente, 1 fatura, 1 check-in, 1 consulta.

| Resultado | Observação |
|---|---|
| | |

---

## 3. Utente existente

Pesquisar o utente do caso 2 → seleccionar sem reescrever dados → atendimento → pagar (se nova visita) ou só encaminhar conforme fluxo do dia.

| Resultado | Observação |
|---|---|
| | |

---

## 4. Utente importado (histórico)

Abrir ficha com aviso de dados anteriores → completar telefone/morada se vazio → Confirmar dados → Novo atendimento → utente já seleccionado no Atendimento rápido.

| Resultado | Observação |
|---|---|
| | |

---

## 5. Marcação + Confirmar chegada

Criar/localizar marcação de hoje → Confirmar chegada → aparece na fila → **não** cria segunda marcação. Repetir Confirmar chegada (idempotente).

| Resultado | Observação |
|---|---|
| | |

---

## 6. Pagamento integral

Fatura 10.000 → pagar 10.000 → saldo 0 → recibo. No Painel/resumo do dia, recebido reflecte o valor.

| Resultado | Observação |
|---|---|
| | |

---

## 7. Redução

Serviço catálogo 10.000 → cobrar 8.000 com motivo → pagar 8.000. Confirmar catálogo ainda mostra 10.000.

| Resultado | Observação |
|---|---|
| | |

---

## 8. Pagamento parcial + saldo

Fatura 10.000 → pagar 6.000 → saldo 4.000 → lista «Com saldo pendente» → pagar 4.000 → saldo 0 → segundo recibo.

| Resultado | Observação |
|---|---|
| | |

---

## 9. Overpayment (negativo)

Com saldo 4.000, tentar 5.000. Confirmar bloqueio na UI e mensagem clara. Nenhum pagamento a mais.

| Resultado | Observação |
|---|---|
| | |

---

## 10. Cancelar fatura

Fatura aberta sem pagamento (ou estado cancelável) → Cancelar → confirmação → deixa de aparecer em saldo activo; registo continua visível no histórico.

| Resultado | Observação |
|---|---|
| | |

---

## 11. Fila

≥2 utentes: «1.º na fila», «2.º na fila»; espera «cerca de … min» ou «sem estimativa»; triagem amarela/verde; prioridade alta; Chamado.

| Resultado | Observação |
|---|---|
| | |

---

## 12. Sem médico disponível

Com utente pago na fila e **sem** médico disponível (ou todos em consulta): tentar atribuir. Esperado: mensagem clara; utente **permanece** na fila; pagamento **não** se perde.

| Resultado | Observação |
|---|---|
| | |

---

## 13. Privacidade (smoke)

Na ficha: não editar alergias/doenças (sem botões clínicos ou erro). Não ver diagnóstico/notas médicas nas consultas da Receção.

| Resultado | Observação |
|---|---|
| | |

---

## 14. Pesquisa

Paciente por nome / telefone / PAC-… . Fatura por nome / FAT-… / n.º processo. Testar 0 e vários resultados.

| Resultado | Observação |
|---|---|
| | |

---

## 15. Portátil Receção (~1366×768)

Repetir Atendimento rápido + pagamento no ecrã real. Botões principais acessíveis; sem overflow que impeça concluir.

| Resultado | Observação |
|---|---|
| | |

---

## 16. Encaminhar utente para médico

1. Seleccionar paciente (Atendimento rápido ou Fila).  
2. Após pagamento, abrir «Encaminhar para médico».  
3. Escolher médico na lista (nome humano; ver Disponível / em espera / Indisponível).  
4. Confirmar encaminhamento.  
5. Na fila da Receção, confirmar coluna «Médico» com o nome correcto.  
6. No perfil do médico escolhido, confirmar que o paciente aparece na fila clínica.  
7. (Opcional) Com outro médico: confirmar que **não** recebe esse paciente como atribuído.

| Resultado | Observação |
|---|---|
| | |

---

## Decisão UAT

| Critério | Sim / Não |
|---|---|
| Nenhum FALHOU em fluxos críticos (2–9, 11–12, 16) | |
| Rececionista concluiu sem ajuda de programador | |
| Pronto para piloto controlado | |

**Assinatura / data:** _______________________
