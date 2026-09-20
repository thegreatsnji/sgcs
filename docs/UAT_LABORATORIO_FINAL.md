# UAT Laboratório — checklist final (SauVida)

**Pré-requisitos:** utilizadores reais LABORATORIO, RECECIONISTA, MÉDICO; catálogo com pelo menos um exame (ex. Hemograma); browser com impressão.

**Gates automatizados:** ver `docs/SPRINT25_LABORATORY_WORKFLOW_HARDENING.md`.

---

## Tarefas (≈12)

### 1. Login laboratório
Entrar como técnico. Confirmar painel com pedidos pendentes e acções rápidas.

### 2. Pedido aguarda regularização
Médico solicita Hemograma. No lab: ver badge «Aguarda regularização». Tentar «Processar» — deve falhar com mensagem clara. Pedido continua na lista.

### 3. Receção regulariza
Receção → Exames lab. Ver utente + exame. Abrir faturação (fluxo existente). Marcar regularizado. Confirmar que **não** nasce pagamento automático.

### 4. Idempotência
Marcar o mesmo pedido regularizado outra vez — sucesso sem duplicar efeitos.

### 5. Lab processa após regularização
Actualizar lista. Badge «Regularizado». Receber → (opcional colheita) → Processar → registar resultado.

### 6. Identificação utente
No formulário de resultado: nome, código, sexo, idade/DN (se existir), médico — sempre visíveis.

### 7. Resultado textual
Exame tipo HCG / texto: conclusão «POSITIVO» sem parâmetros numéricos. Guardar.

### 8. Não validado
Antes de validar: médico vê estado sem valores. Receção **não** vê valores clínicos.

### 9. Validar
Confirmar diálogo. Após validar: médico vê resultado. Resultado fica read-only.

### 10. Marcar entregue / imprimir
Opcional: «Marcar como entregue». Imprimir só após validado — documento com clínica, utente, exame, valores/conclusão, validador. Reimprimir sem mudar estado.

### 11. Múltiplos exames
Dois pedidos no mesmo paciente — estados e regularização independentes; validar A não valida B.

### 12. Prioridade e pesquisa
Pedido EMERGENCY aparece antes de NORMAL na lista pendente. Pesquisar por nome/exame/código.

### 13. Histórico migrado (se houver paciente importado)
Abrir histórico anterior — sem Validar/Publicar/Editar em registos migrados.

### 14. Privacidade lab
Confirmar que técnico **não** acede a faturação completa, pagamentos, nem edição clínica.

---

## Critério de sucesso

Todas as tarefas 1–12 passam em ambiente real. Pendências de hardware (impressora) podem ficar anotadas sem bloquear `LABORATORY_READY_FOR_UAT`.
