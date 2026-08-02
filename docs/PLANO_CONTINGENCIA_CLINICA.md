# Plano de contingência clínica — SGCS SauVida

Usar quando o sistema ou infraestrutura falham **durante o piloto**. Não substitui backup nem plano de recuperação de TI.

## Contactos (preencher na clínica)

| Função | Nome | Telefone | Disponibilidade |
|--------|------|----------|-----------------|
| Suporte técnico SGCS | | | |
| Administrador clínica | | | |
| Director clínico | | | |
| ISP / rede | | | |

---

## Cenários

### 1. Falha de Internet

| Acção imediata | Registo manual temporário (papel) | Reconciliação |
|----------------|-------------------------------------|---------------|
| Confirmar se piloto é local (LAN) vs cloud | Ficha papel: paciente, serviço, valor, hora, operador | Inserir faturas/pagamentos no SGCS quando rede voltar |
| Usar hotspot só se política clínica permitir | Numerar talões manuais | Conferir totais do dia com director |

### 2. Falha de energia

| Acção | Notas |
|-------|-------|
| UPS mantém servidor? | Se não, aguardar energia; não forçar desligamento abrupto |
| Atendimento | Modo papel até energia + sistema estáveis |
| Dados | Após arranque, verificar integridade BD (admin) |

### 3. Servidor / aplicação indisponível

| Acção | Notas |
|-------|-------|
| Verificar health endpoint | |
| Reinício controlado (Docker/systemd) | Registar hora |
| Restauro backup | Último backup validado; ver runbook backup |
| Comunicar pausa atendimento digital | Director + recepção |

### 4. Impressora indisponível

| Acção | Notas |
|-------|-------|
| Recibo digital / email se política permitir | |
| Recibo manual numerado | Ligar n.º manual ao ID fatura no SGCS depois |
| Segunda via | Só após sistema disponível |

### 5. Perda de sessão (logout inesperado)

| Acção | Notas |
|-------|-------|
| Voltar a entrar | JWT refresh; não partilhar sessão |
| Trabalho não guardado | Repetir passo; verificar duplicados antes de novo pagamento |

### 6. Erro de pagamento

| Acção | Notas |
|-------|-------|
| Não repetir pagamento sem verificar estado da fatura | |
| Anotar ID fatura e valor | Director/financeiro confirma |
| Corrigir no SGCS com permissão adequada | Auditoria activa |

### 7. Duplicação de recibo

| Acção | Notas |
|-------|-------|
| Identificar n.º recibo e fatura | |
| Segunda via só com justificação | |
| Não anular papel sem procedimento director |

### 8. Dados não sincronizados (vários postos)

| Acção | Notas |
|-------|-------|
| Actualizar página (F5) | |
| Um único posto regista pagamento crítico | Evitar edição paralela da mesma fatura |

---

## Registo manual temporário (mínimo)

- Data/hora  
- N.º processo ou nome paciente  
- Serviço e valor (FCFA)  
- Pago / parcial / pendente  
- Operador (rubrica)  
- N.º talão manual  

## Reconciliação posterior

1. Responsável recepção + administrador.  
2. Inserir no SGCS por ordem cronológica.  
3. Conferir totais com caixa do dia.  
4. Arquivar folhas assinadas.

## Comunicação

- Staff: quadro na recepção «Sistema em contingência — usar ficha papel».  
- Director: informado em &lt; 15 min em falha &gt; 30 min.
