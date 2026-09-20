# Auditoria dos 5 fluxos operacionais — piloto clínico SauVida

**Data:** 2026-08-19  
**Âmbito:** Receção, Médico, Laboratório, Stock de urgência, Direção  
**Princípio:** só alterar o que impede a clínica de trabalhar depressa, sem formação técnica.

Os tempos-alvo abaixo são **metas operacionais**, não testes rígidos. Se o atraso for de rede/backend, registar em separado do UX.

---

## 1. Receção

### Passos actuais (atendimento normal)

1. Painel receção → **Iniciar atendimento** (`/reception/atendimento?passo=1`)
2. Pesquisar utente (nome, telefone ou n.º de processo; ≥ 2 caracteres)
3. Seleccionar utente → passo 2 (triagem / check-in)
4. Confirmar propósito da visita e check-in → passo 3
5. **Criar fatura e cobrar** → ecrã de fatura (serviço + eventual redução)
6. **Guardar e receber pagamento** (acção principal neste retorno)
7. Confirmar pagamento integral → recibo (imprimir)
8. Voltar ao atendimento → passo 4 → notificar / encaminhar médico

Pagamento parcial e redução de preço **permanecem conceitos distintos**. A receção exige pagamento do valor cobrado de hoje antes de encaminhar; redução altera o valor cobrado, não o estado de saldo.

### Interacções (aproximado)

| Cenário | Cliques / teclas | Mudanças de ecrã |
|---|---:|---:|
| Utente conhecido, 1 serviço, pagamento integral, sem redução | ~12–16 | 3 (atendimento → fatura → pagamento/recibo → atendimento) |
| Com redução autorizada | +2–4 | igual |
| Pagamento incompleto | +2–4 | 1 extra (completar pagamento) |
| Utente novo | + ficha completa | 1 extra |

### Problemas encontrados

| Problema | Gravidade | Decisão |
|---|---|---|
| Pesquisa sem foco automático — a rececionista tinha de clicar no campo | Média | **Corrigido:** `autoFocus` no campo de pesquisa |
| Na fatura vinda da receção, «Guardar fatura» era o botão primário; o fluxo SauVida é cobrar antes da consulta | Alta | **Corrigido:** com `retorno`, primário = «Guardar e receber pagamento» |
| Pagamento e fatura em ecrãs separados | Baixa | **Não alterar:** já ligados pelo botão de atendimento; endpoints existentes; não duplicar módulo |
| Check-in pode falhar sem médico disponível | Conhecida | **Não alterar agora:** falhas pré-existentes de testes; documentadas no relatório |

### Melhoria proposta vs risco

| Melhoria | Risco | Feito? |
|---|---|---|
| Foco na pesquisa | Nulo | Sim |
| Primário «receber pagamento» só com retorno da receção | Baixo (fatura avulsa mantém «Guardar fatura») | Sim |
| Fundir fatura+pagamento num único ecrã | Médio (duplicação / contratos) | Não |

### Fluxo final

Pesquisar → seleccionar → triagem → criar fatura e cobrar → (redução se autorizada) → pagamento → recibo → encaminhar médico.

A rececionista não precisa de perceber a arquitectura: o stepper diz **Triagem → pagamento e recibo → só depois médico**.

---

## 2. Médico

### Passos actuais

1. Painel médico: vê **próximo paciente** e KPIs
2. **Atender agora** inicia a consulta (`POST .../start/`) e abre o prontuário  
   ou Fila → cartão **Próximo utente** → **Atender agora**
3. Cabeçalho: identidade, alergias, motivo/queixa da receção
4. Barra lateral: consultas SGCS + **histórico do utente** (importado vs SGCS)
5. Preencher vitais / SOAP / diagnósticos; pedir laboratório; concluir

### Interacções (aproximado)

| Cenário | Interacções | Ecrãs |
|---|---:|---:|
| Abrir próximo paciente a partir do painel | 1 clique | 1 |
| Abrir a partir da fila (cartão) | 1 clique | 1 |
| Pedir laboratório na consulta | 2–4 | 0 (separador) |

### Problemas encontrados

| Problema | Gravidade | Decisão |
|---|---|---|
| «Iniciar consulta» no painel abria a ficha **sem** `start` — estado podia ficar em espera | Alta | **Corrigido:** `Atender agora` chama `start` |
| Fila sem destaque do próximo utente | Média | **Corrigido:** cartão no topo |
| Histórico importado pouco distinguível do SGCS | Alta (clínico) | **Corrigido:** selo «Histórico anterior» / «SGCS»; timeline compacta na consulta |
| Navegação extra para ver histórico migrado | Média | **Corrigido:** visível na barra lateral da consulta |

### Melhoria vs risco

| Melhoria | Risco | Feito? |
|---|---|---|
| `start` no painel | Baixo; se já estiver em consulta, abre a ficha | Sim |
| Selo de proveniência | Nulo (só UI) | Sim |
| Novo ecrã de histórico | Alto | Não |

### Fluxo final

Ver próximo utente → Atender agora → prontuário (motivo + histórico distinguível) → dados clínicos → laboratório se preciso → concluir.

---

## 3. Laboratório

### Passos actuais

1. Pedidos pendentes (ou painel → pedidos)
2. Abrir pedido: paciente, exames, médico, estado, fluxo
3. Receber / colher / processar
4. Introduzir resultado
5. **Validar resultado** (confirmação)
6. Publicar ao médico; imprimir / consultar

Histórico laboratorial textual migrado **não** é convertido em resultado estruturado.

### Interacções (aproximado)

| Cenário | Interacções |
|---|---:|
| Encontrar pedido na lista | 1–2 (filtro/pesquisa existente) |
| Processar + resultado simples + validar | ~8–12 |

### Problemas encontrados

| Problema | Gravidade | Decisão |
|---|---|---|
| Médico solicitante não visível na tabela | Média | **Corrigido:** coluna Médico |
| Validar resultado com um clique (erro fácil) | Alta | **Corrigido:** `confirm` antes de validar |
| Estados / paciente / exame | — | Já claros; sem redesenho |

### Fluxo final

Pendentes → abrir (paciente + exame + médico visíveis) → processar → resultado (rascunho distinto) → confirmar validação → imprimir/consultar.

---

## 4. Stock de urgência

### Passos actuais

1. Lista (pesquisa com foco)
2. Ver Nome, quantidade actual, unidade, mínimo, estado
3. **Entrada** ou **Saída** → quantidade + confirmar
4. **Histórico** por item ou global

Quantidade actual **não** é editável na tabela. Toda a alteração gera `MovimentoStockUrgencia`. Stock negativo bloqueado no serviço e no modal de saída.

### Interacções (aproximado)

| Cenário | Interacções | Meta |
|---|---:|---|
| Entrada/saída com item visível | 3 (acção → quantidade → confirmar) | ≤ 30 s |

### Problemas encontrados

| Problema | Gravidade | Decisão |
|---|---|---|
| Colunas Apresentação e Validade na tabela principal | Média (ruído) | **Corrigido:** colunas pedidas só |
| Estados técnicos (`DISPONIVEL`, `STOCK_BAIXO`…) | Média | **Corrigido:** Normal / Stock baixo / Sem stock |
| Saída maior que o stock no UI | Média | **Corrigido:** botão bloqueado + mensagem |
| Botões «+ Entrada» / «− Saída» | Baixa | **Corrigido:** Entrada / Saída / Histórico |

Não adicionados: fornecedores, POS, margem, compras, farmácia comercial, lotes.

### Fluxo final

Pesquisar → Entrada ou Saída → confirmar quantidade (sem negativo) → histórico se necessário.

---

## 5. Direção (telemóvel em primeiro lugar)

### Passos actuais

Painel executivo já existente: receita hoje/mês, pagamentos hoje, faturas em dívida, utentes, consultas, laboratório, serviços mais utilizados, alertas.

### Problemas encontrados

| Problema | Gravidade | Decisão |
|---|---|---|
| Sem alerta de stock de urgência no painel | Média | **Corrigido:** cartão Stock baixo / Sem stock via `/stock/dashboard/` existente (se o perfil tiver permissão; 403 não bloqueia o resto) |
| Histórico financeiro migrado | — | **Não alterar:** isolamento já feito na Sprint 21; não criar métricas novas |
| Dashboard «mais bonito» / mais gráficos | — | **Não fazer** |

### Fluxo final

Abrir painel → ler KPIs operacionais/financeiros actuais + stock de urgência se disponível. Sem módulo novo.

---

## 6. O que não foi alterado (já suficiente)

- Stepper de 4 passos da receção e gate de pagamento antes do médico
- Separação redução vs pagamento parcial
- Contratos API, JWT, RBAC, modelos, regras clínicas
- Catálogo, importação de stock, migração histórica, cores/tipografia globais
- Conversão de histórico lab. textual em resultado estruturado

## 7. Tempos-alvo (UAT presencial)

| Tarefa | Meta |
|---|---|
| Pesquisar paciente | ≤ 15 s |
| Atendimento normal (fim-a-fim) | ≤ 2 min |
| Adicionar serviço à fatura | ≤ 15 s |
| Registar pagamento | ≤ 30 s |
| Emitir recibo | ≤ 30 s |
| Entrada/saída de stock | ≤ 30 s |
| Abrir próximo paciente (médico) | ≤ 15 s |
| Encontrar pedido laboratorial | ≤ 15 s |
