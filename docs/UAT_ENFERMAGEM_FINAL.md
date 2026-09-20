# UAT Enfermagem — checklist final (SauVida)

**Pré-requisitos:** utilizadores reais ENFERMEIRO, RECECIONISTA, MÉDICO; pelo menos um utente; stock de urgência com alguns itens. Após deploy, correr `python manage.py seed_rbac`.

**Gates automatizados:** ver `docs/SPRINT26_NURSING_WORKFLOW_HARDENING.md`.

---

## Tarefas

### 1. Login enfermeiro
Entrar. Painel mostra stock baixo, sem stock, próximos da validade, expirados. Menu: Painel, Triagem, Stock, Pacientes. **Sem** fila, atendimento, exames lab, faturação.

### 2. Triagem
Nova triagem → pesquisar utente → cor + TA + temperatura + peso + prioridade → guardar. Confirmar que entra na fila (a Receção vê).

### 3. Sinais vitais no médico
Receção encaminha para médico. Médico abre consulta e vê **Sinais vitais da triagem**. Confirmar que o original da triagem não foi alterado.

### 4. Edição clínica indevida
Como enfermeiro, tentar alterar diagnóstico / SOAP / plano / prescrição — deve falhar (403 / sem ecrã).

### 5. Stock inicial
Criar item com quantidade 0. Badge «Stock inicial por confirmar». **Definir stock inicial** (unidade, quantidade, mínimo, validade opcional). Segunda tentativa deve falhar.

### 6. Entrada
Item existente → Entrada + quantidade → ver Antes / Entrada / Depois. Histórico: «Entrada».

### 7. Saída
Saída com quantidade ≤ stock. Tentar quantidade > stock — bloquear. Item **não** expirado.

### 8. Ajuste
Mais acções → Ajustar stock. Sistema vs contagem física, diferença, motivo. Confirmar movimento «Ajuste».

### 9. Perda / expiração
Registar perda (quantidade + motivo EXPIRADO / DANIFICADO / PERDIDO / OUTRO). Stock reduz. Histórico: «Perda / Expiração». Datas em DD/MM/AAAA HH:mm.

### 10. Item expirado
Item com validade ontem e quantidade > 0: badge **Expirado** (não «Sem stock»). Saída desactivada / mensagem «Este item está expirado e não pode ser utilizado.» Perda permitida.

### 11. Duplicado
Tentar criar o mesmo nome + apresentação. Mensagem «Já existe um item semelhante» e opção de abrir o existente.

### 12. Regularização lab
Pedido lab a aguardar regularização. Enfermeiro **não** consegue marcar regularizado. Receção continua a conseguir.

### 13. Permissões
Enfermeiro não fatura, não recebe pagamento, não gere fila, não encaminha para médico, não confirma chegada de marcações, não edita catálogo/preços, não gere utilizadores.

---

## Perguntas clínicas (não bloquear UAT técnico)

**DECISÃO_CLINICA_PENDENTE**

- Quem é o responsável principal pela triagem: Receção ou Enfermagem?
- O enfermeiro precisa de registar curativos?
- Injecções?
- Soroterapia?
- Administração de medicamento (além da Saída de stock)?
- Nota de enfermagem?

Só implementar depois de resposta real da clínica.

---

## Critério de sucesso

Tarefas 1–13 passam em ambiente real. As perguntas clínicas podem ficar em aberto sem impedir `NURSING_READY_FOR_UAT`.
