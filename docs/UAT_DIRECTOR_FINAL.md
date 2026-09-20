# UAT — Director (final)

**Perfil:** DIRECTOR  
**Estado alvo:** `DIRECTOR_READY_FOR_UAT`  
**Ambiente:** demo com `seed_rbac` + dados fictícios de faturação  
**Viewport sugerido:** 390px (telemóvel) + desktop

## Pré-condições

1. `python manage.py migrate`
2. `python manage.py seed_rbac`
3. Login: utilizador DIRECTOR (ex. demo)

---

## Tarefas

### 1. Abrir painel sem bloqueio
- Ir a `/dashboard/director`
- **Esperado:** painel carrega; sem skeleton infinito; Network **sem** 403 em `/dashboard/director/`
- Confirmar que **não** há pedido a `/dashboard/reception/`

### 2. KPIs financeiros no 1.º ecrã (390px)
- Sem scroll excessivo, identificar: Faturado, Recebido, Saldo pendente, Reduções
- Valores em **FCFA**

### 3. Período — Hoje / Semana / Mês
- Alternar os três botões
- **Esperado:** label do período em português (`dd/mm/aaaa` ou intervalo)

### 4. Período personalizado
- Escolher Personalizado → datas → Aplicar
- Sem datas: não deve aplicar o mês em silêncio
- Com datas: KPIs actualizam ao intervalo

### 5. Fim do dia (dados fictícios)
- Com fatura 100 000 e pagamento 70 000 no dia:
  - Faturado = 100 000 FCFA
  - Recebido = 70 000 FCFA
  - Saldo pendente = 30 000 FCFA (montante, **não** “1 fatura”)

### 6. Pagamento parcial
- Fatura 10 000, pagamento 6 000 → PARCIAL
  - Faturado 10 000 / Recebido 6 000 / Saldo 4 000

### 7. Histórico migrado
- PatientHistory financeiro fictício no dia
- **Esperado:** não altera Faturado / Recebido / Saldo / Reduções

### 8. Utentes e consultas
- Ver «Utentes atendidos» (check-ins concluídos) e consultas do período

### 9. Laboratório (agregados)
- Com pedidos a aguardar regularização / validação
- **Esperado:** contagens no cartão Lab; **sem** valores/conclusões clínicas

### 10. Stock crítico
- Ver stock baixo / sem / próximos / expirados
- Abrir `/stock`: **sem** botões Entrada / Saída / Ajuste / Perda

### 11. Faturação read-only
- Abrir fatura com saldo: **sem** «Registar pagamento» / Cancelar
- POST pagamento (API ou tentativa UI) → bloqueado

### 12. RBAC clínico
- Tentar SOAP / prescrição / validar lab → 403
- Pacientes: ver lista OK; editar → bloqueado

### 13. Navegação
- Menu só com áreas relevantes (Painel, Relatórios, Faturação, Pacientes, Stock)
- Sem links que terminem em 403 de Receção/clínica operacional

### 14. Erro parcial
- (Opcional) Simular falha de uma secção: mensagem «Não foi possível carregar este indicador.»; restantes OK

### 15. Relatórios
- De Painel → Relatórios: abre sem 403
- Exportações existentes (PDF/Excel/CSV) se disponíveis; stubs não apresentados como funcionais

---

## Resultado UAT

| # | Passou? | Notas |
|---|---------|-------|
| 1–15 |  |  |

**Decisão:** DIRECTOR_READY_FOR_UAT / DIRECTOR_NEEDS_FIXES
