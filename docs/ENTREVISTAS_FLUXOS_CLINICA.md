# Guia de entrevistas — Fluxos da clínica SauVida

**Projecto:** SGCS — Sistema de Gestão Clínica SauVida  
**Objectivo:** Recolher informação da proprietária e da equipa técnica sobre o funcionamento real da clínica, antes de concluir o sistema.

> **Sprint 15:** Após visita presencial, os fluxos consolidados, lacunas, catálogo de preços e roadmap por versão estão em **[SPRINT15/](SPRINT15/README.md)** e **[SPRINT15_REPORT.md](SPRINT15_REPORT.md)**. Use este guia para sessões adicionais ou UAT; preencha as tabelas abaixo quando necessário.

**Idioma da interface:** Português  
**Utilizadores previstos:** 1 Administrador, 1 Director, 2 Médicos, 1 Rececionista, 1 Técnico de Laboratório (sem perfil FINANCEIRO)

---

## 1. Quem entrevistar

| Pessoa | Foco principal |
|--------|----------------|
| **Proprietária / Director** | Finanças, relatórios, aprovações, visão diária da clínica |
| **Rececionista** | Check-in, fila, marcações, registo de pacientes |
| **Médicos (2)** | Consulta, prontuário clínico, prescrições, pedidos de laboratório, seguimento |
| **Técnico de laboratório** | Colheita → processamento → validação → publicação → notificação ao médico |
| **Administrador / TI** | Utilizadores, cópias de segurança, segurança, quem faz o quê |

> O perfil **FINANCEIRO** existe no sistema apenas para expansão futura. As responsabilidades financeiras são do **Director** — não é necessário entrevistar um utilizador FINANCEIRO.

---

## 2. Perguntas por área

### 2.1 Jornada do paciente

- Como chega o paciente: sem marcação, com consulta agendada, encaminhamento?
- O que se regista no primeiro contacto e o que fica para depois?
- Utilizam seguros? Quais os campos obrigatórios?
- Quem pode ver o prontuário clínico completo e quem vê apenas dados básicos?

**Registar respostas:**

| Pergunta | Resposta | Responsável |
|----------|----------|-------------|
| | | |
| | | |

---

### 2.2 Receção

- Passos exactos do check-in (procurar paciente → prioridade → fila → médico)?
- Como são tratadas urgências na fila?
- Quando o paciente vai para faturação antes da consulta?
- Imprimem algo na receção (senha, ficha do paciente)?

**Registar respostas:**

| Pergunta | Resposta | Responsável |
|----------|----------|-------------|
| | | |
| | | |

---

### 2.3 Consultas e prontuário clínico (PCE)

- Fluxo típico: sinais vitais → SOAP → diagnóstico → prescrição → laboratório → alta?
- Pode editar-se a consulta depois de concluída?
- Prescrições: só papel, ou também digital/impressão?
- Seguimentos: quem agenda — médico ou receção?

**Registar respostas:**

| Pergunta | Resposta | Responsável |
|----------|----------|-------------|
| | | |
| | | |

---

### 2.4 Laboratório

- Quem cria o pedido laboratorial (só médico ou também receção)?
- Passos: pedido → colheita → processamento → validação → publicação?
- Quem valida os resultados antes do médico ver?
- Como o médico deve ser notificado (no sistema, SMS, e-mail, ambos)?

**Registar respostas:**

| Pergunta | Resposta | Responsável |
|----------|----------|-------------|
| | | |
| | | |

---

### 2.5 Faturação e pagamentos

- Preço da consulta: fixo, por serviço, por médico/especialidade?
- Quando se cobra: antes da consulta, depois, ou misto?
- Pagamentos parciais e recibos — são frequentes?
- Quem aprova orçamentos? Só o Director?

**Registar respostas:**

| Pergunta | Resposta | Responsável |
|----------|----------|-------------|
| | | |
| | | |

---

### 2.6 Financeiro (Director)

- Caixa: uma por pessoa ou uma por clínica?
- Categorias de despesas que usam de facto
- Relatórios necessários: caixa diário, mensal, lucro, desempenho dos médicos, etc.

**Registar respostas:**

| Pergunta | Resposta | Responsável |
|----------|----------|-------------|
| | | |
| | | |

---

### 2.7 Relatórios e painéis

- O que a proprietária consulta todas as manhãs?
- Exportações: PDF para contabilidade, Excel para análise?
- Existem obrigações legais ou relatórios exigidos na Guiné-Bissau?

**Registar respostas:**

| Pergunta | Resposta | Responsável |
|----------|----------|-------------|
| | | |
| | | |

---

### 2.8 Utilizadores e acessos

- Confirmar os 6 utilizadores: 1 Admin, 1 Director, 2 Médicos, 1 Receção, 1 Lab
- Alguém mais no futuro (enfermeiro, farmácia)?
- Conta individual por pessoa ou partilham credenciais?

**Registar respostas:**

| Pergunta | Resposta | Responsável |
|----------|----------|-------------|
| | | |
| | | |

---

### 2.9 Idioma, marca e documentos

- Nome oficial da clínica, NIF, morada, telefone, logótipo para impressões
- Moeda sempre em FCFA?
- Assinatura/carimbo em receitas, resultados de laboratório, faturas?

**Registar respostas:**

| Pergunta | Resposta | Responsável |
|----------|----------|-------------|
| | | |
| | | |

---

### 2.10 Prioridades: obrigatório vs desejável

Pedir que classifiquem cada item:

| Prioridade | Significado |
|------------|-------------|
| **Obrigatório para arranque** | Sem isto a clínica não pode usar o sistema |
| **Pode esperar** | Útil, mas depois do go-live |
| **Não é necessário** | Não faz falta |

**Lista sugerida para classificar:**

- [ ] Registo e pesquisa de pacientes  
- [ ] Check-in e fila de espera  
- [ ] Marcação e agenda médica  
- [ ] Prontuário clínico (SOAP, diagnósticos, prescrições)  
- [ ] Pedidos e resultados de laboratório  
- [ ] Orçamentos, faturas, pagamentos, recibos  
- [ ] Caixa e movimentos financeiros  
- [ ] Relatórios e dashboard executivo  
- [ ] Notificações internas  
- [ ] Impressão de documentos (ficha, receita, resultado, fatura, recibo)  
- [ ] Recuperação de palavra-passe  
- [ ] Seguros do paciente  
- [ ] Catálogo CID-10  

**Registo de prioridades:**

| Funcionalidade | Obrigatório | Pode esperar | Não necessário | Notas |
|----------------|:-----------:|:------------:|:--------------:|-------|
| | | | | |
| | | | | |

---

## 3. Lacunas já conhecidas no sistema (validar com a clínica)

Estes pontos foram identificados na auditoria pré-Sprint 14. Use-os para confirmar expectativas:

| Tema | Estado actual | Pergunta para a clínica |
|------|---------------|-------------------------|
| Recuperação de palavra-passe | Não implementado | Os funcionários precisam de redefinir a palavra-passe sozinhos? |
| Cancelamento de consulta | API pronta, botão na UI em falta | Quem pode cancelar e em que situações? |
| Seguro do paciente | Backend pronto, sem ecrã | Utilizam seguros? Quais os dados obrigatórios? |
| CID-10 | Texto livre | Precisam de pesquisa/catálogo de diagnósticos? |
| Notificação médico (lab) | Tarefa Celery em stub | SMS, e-mail ou só notificação no sistema? |
| Configurações (alguns ecrãs) | Parcialmente placeholder | O que querem configurar eles próprios? |
| Layouts de impressão | Estrutura pronta, falta ligar aos ecrãs | Podem fornecer exemplos de papel usado hoje? |

**Decisões registadas:**

| Tema | Decisão | Data | Quem decidiu |
|------|---------|------|--------------|
| | | | |
| | | | |

---

## 4. Como conduzir as sessões

### 4.1 Preparação

1. Ambiente de demonstração com dados fictícios:
   ```bash
   docker compose up -d
   docker exec sgcs-backend python manage.py seed_rbac
   docker exec sgcs-backend python manage.py seed_demo
   ```
2. Credenciais demo: ver [DEMO_DATA.md](./DEMO_DATA.md)
3. Imprimir ou partilhar este documento com notas por entrevistado

### 4.2 Método recomendado

| Passo | Acção |
|-------|--------|
| 1 | **Observar** meio dia na clínica, se possível (receção → consulta → lab → pagamento) |
| 2 | **Entrevistar** cada perfil (30–45 min) com o sistema demo aberto |
| 3 | **Registar** decisões com data e nome de quem decidiu |
| 4 | **Priorizar** 10–15 fluxos que têm de funcionar perfeitamente no arranque |

### 4.3 Roteiro por sessão (30–45 min)

1. Apresentação do objectivo (5 min)  
2. Demonstração do módulo do perfil (10 min)  
3. Perguntas da secção correspondente (15–20 min)  
4. Priorização obrigatório / pode esperar (5 min)  
5. Recolha de documentos ou exemplos em papel (5 min)

---

## 5. Entregável após as entrevistas

Após reunir a informação, consolidar num único documento (ou actualizar o SRS) com:

- [ ] Fluxos por perfil (receção, médico, laboratório, director)  
- [ ] Lista **obrigatório para go-live** vs **fase 2**  
- [ ] Amostras de documentos impressos (ficha, receita, resultado, fatura, recibo)  
- [ ] Dados oficiais da clínica (nome, NIF, contactos, logótipo)  
- [ ] Perguntas em aberto e responsáveis por responder  

**Modelo de registo de decisão:**

```
Data: _______________
Participantes: _______________
Tema: _______________
Decisão: _______________
Impacto no SGCS: _______________
Prioridade: [ ] Go-live  [ ] Fase 2  [ ] Não necessário
```

---

## 6. Checklist mínimo para go-live

Marcar após validação com a proprietária:

| # | Fluxo | Validado | Notas |
|---|--------|:--------:|-------|
| 1 | Login por perfil e menu correcto | | |
| 2 | Registo e pesquisa de paciente | | |
| 3 | Check-in e fila de espera | | |
| 4 | Marcação / agenda do dia | | |
| 5 | Consulta e prontuário clínico | | |
| 6 | Pedido e resultado de laboratório | | |
| 7 | Orçamento / fatura / pagamento (FCFA) | | |
| 8 | Caixa e movimentos (Director) | | |
| 9 | Relatório ou dashboard executivo | | |
| 10 | Impressão dos documentos principais | | |
| 11 | Textos da interface em português | | |
| 12 | Cópias de segurança e utilizadores reais | | |

---

## 7. Documentos relacionados

| Documento | Conteúdo |
|-----------|----------|
| [AUDITORIA_PRE_SPRINT14.md](./AUDITORIA_PRE_SPRINT14.md) | Estado técnico actual do sistema |
| [DEMO_DATA.md](./DEMO_DATA.md) | Utilizadores e dados de demonstração |
| [ROLE_DASHBOARDS.md](./ROLE_DASHBOARDS.md) | Painéis por perfil |
| [USER_TESTING_GUIDE.md](./USER_TESTING_GUIDE.md) | Guia de testes por perfil |
| [SPRINT15_REPORT.md](./SPRINT15_REPORT.md) | Sprint 15 — fluxos, catálogo, roadmap |
| [SPRINT15/README.md](./SPRINT15/README.md) | Índice documentação Sprint 15 |
| [SRS/PRODUCT_ROADMAP.md](./SRS/PRODUCT_ROADMAP.md) | Roadmap do producto |

---

*Documento criado para apoio à recolha de requisitos com a clínica SauVida. Preencher as tabelas durante ou após cada entrevista.*
