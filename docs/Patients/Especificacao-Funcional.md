# Especificação Funcional — Módulo de Gestão de Pacientes

**Projeto:** SGCS — Sistema de Gestão Clínica SauVida  
**Sprint:** 4  
**Versão do documento:** 1.0  
**Data:** Julho 2026

---

## 1. Visão Geral do Módulo

O módulo de **Gestão de Pacientes** é responsável pelo ciclo de vida do registo clínico de cada utente da SauVida: desde o primeiro contacto na receção até à consulta dos seus dados por médicos, enfermeiros, laboratório e equipa financeira.

### Posição no ecossistema

O paciente é a **entidade raiz** do domínio clínico. Nenhum outro módulo operacional (Receção, Consultas, Laboratório, Faturação) pode funcionar sem um registo de paciente válido e identificável.

### Âmbito da Sprint 4

| Incluído | Excluído (sprints futuras) |
|----------|---------------------------|
| Registo demográfico e de contacto | Prontuário eletrónico completo |
| Identificação única (nº processo + documento) | Prescrições e diagnósticos |
| Pesquisa, listagem e ficha resumo | Integração com sistemas externos (HL7/FHIR) |
| CRUD com soft delete | Agendamento (módulo Consultas) |
| RBAC e auditoria | Pedidos de laboratório |
| Exportação básica | Faturação detalhada |

### Utilizadores do módulo

| Perfil | Interação principal |
|--------|---------------------|
| **Rececionista** | Registo, pesquisa, edição de dados administrativos |
| **Médico** | Consulta e edição de dados clínicos relevantes |
| **Enfermeiro** | Consulta de ficha |
| **Laboratório** | Consulta para associação a exames |
| **Financeiro** | Consulta para faturação |
| **Administrador** | Gestão completa, exportação, desativação |

---

## 2. Objetivos

### Objetivos de negócio

1. **Centralizar** a informação do utente num único registo fiável e pesquisável.
2. **Eliminar duplicações** de pacientes através de validação de identificadores.
3. **Garantir rastreabilidade** de quem acedeu ou alterou dados sensíveis.
4. **Preparar integrações** com os módulos clínicos e financeiros sem retrabalho.

### Objetivos técnicos

1. Implementar API REST em `/api/v1/patients/` seguindo os padrões do módulo `users`.
2. Reutilizar infraestrutura transversal: RBAC, auditoria, paginação, respostas envelope, soft delete.
3. Entregar frontend React com listagem, formulário e ficha de detalhe.
4. Manter **compatibilidade total** com autenticação JWT e módulos existentes.
5. Alinhar tipos TypeScript já definidos em `types/patient.ts` com o contrato API final.

### Objetivos de qualidade

- Tempo de resposta da listagem < 500 ms (até 10 000 registos indexados).
- Cobertura de testes backend ≥ 80% no módulo `patients`.
- Zero endpoints sem proteção RBAC.
- 100% das mutações com registo de auditoria.

---

## 3. Regras de Negócio

### Identificação e unicidade

| ID | Regra |
|----|-------|
| RN-01 | Cada paciente recebe um **número de processo clínico** automático e imutável (formato: `PAC-AAAA-NNNNN`). |
| RN-02 | O `document_number` (BI, passaporte ou outro) deve ser **único** quando preenchido. |
| RN-03 | A combinação `first_name + last_name + birth_date + phone` gera **alerta de possível duplicado** (não bloqueia, exige confirmação). |
| RN-04 | Pacientes sem documento podem ser registados (ex.: urgências), mas o campo fica marcado como pendente. |

### Dados obrigatórios

| ID | Regra |
|----|-------|
| RN-05 | Campos obrigatórios no registo: `first_name`, `last_name`, `gender`, `birth_date`, `phone`. |
| RN-06 | `email` é opcional; se preenchido, deve ser válido e único por paciente ativo. |
| RN-07 | Menores de 18 anos exigem **responsável legal** (nome + telefone) no registo. |

### Ciclo de vida

| ID | Regra |
|----|-------|
| RN-08 | Pacientes são **desativados** (soft delete), nunca removidos fisicamente da base de dados. |
| RN-09 | Paciente com consultas, exames ou faturas ativas **não pode ser eliminado** — apenas desativado. |
| RN-10 | Reativação de paciente desativado requer permissão `patients.edit` e gera auditoria `PATIENT_ACTIVATE`. |
| RN-11 | Apenas `ADMINISTRADOR` ou utilizador com `patients.delete` pode desativar pacientes. |

### Privacidade e acesso

| ID | Regra |
|----|-------|
| RN-12 | Consulta de ficha completa requer `patients.view`. |
| RN-13 | Edição de dados demográficos: `patients.edit` (Rececionista, Médico, Admin). |
| RN-14 | Exportação e impressão requerem `patients.export` / `patients.print` respetivamente. |
| RN-15 | Acesso a dados sensíveis (documento, morada) é auditado com `PATIENT_VIEW` quando configurado. |

### Validações de campo

| ID | Regra |
|----|-------|
| RN-16 | `phone` validado pelo padrão existente: `+?[0-9]{7,15}` (`core.validators.validate_phone_number`). |
| RN-17 | `birth_date` não pode ser futura nem indicar idade superior a 120 anos. |
| RN-18 | `gender` aceita valores `M`, `F`, `O` (alinhado com modelo `User`). |
| RN-19 | Datas apresentadas e devolvidas no formato `DD/MM/YYYY` na API. |

### Operacionais

| ID | Regra |
|----|-------|
| RN-20 | Listagem paginada com 20 registos por página (configurável até 100). |
| RN-21 | Pesquisa textual em `full_name`, `document_number`, `phone`, `patient_number`. |
| RN-22 | Ordenação padrão: `last_name`, `first_name`. |
| RN-23 | Interface em **português**; mensagens de erro claras e acionáveis. |

---

## 4. Fluxo do Paciente

### 4.1 Registo na receção

```
Chegada → Pesquisa (nome/doc/telefone) → Duplicado?
  ├─ Sim  → Abrir ficha existente
  └─ Não  → Formulário de registo → Validação → Gravar → Nº processo gerado → Ficha
```

### 4.2 Consulta de ficha

```
Pesquisa na listagem → Selecionar paciente → Ficha resumo
  ├─ Dados demográficos
  ├─ Contactos
  ├─ Estado (ativo/inativo)
  └─ Atalhos futuros: consultas, exames, faturas
```

### 4.3 Atualização

```
Abrir ficha → Editar → Validação → Gravar → Auditoria
  └─ Conflito de documento duplicado → Erro 409 com mensagem
```

### 4.4 Desativação

```
Solicitar desativação → Verificar dependências
  ├─ Com dependências ativas → Apenas marcar inativo (is_active=false)
  └─ Sem dependências       → Soft delete (deleted_at preenchido)
```

### 4.5 Estados do paciente

| Estado | `is_active` | `deleted_at` | Visível na listagem padrão |
|--------|-------------|--------------|----------------------------|
| Ativo | `true` | `null` | Sim |
| Inativo | `false` | `null` | Com filtro |
| Eliminado (soft) | `false` | timestamp | Apenas admin com filtro |

---

## 5. Casos de Uso

### UC-01 — Registar novo paciente

| Campo | Valor |
|-------|-------|
| **Ator** | Rececionista |
| **Pré-condição** | Utilizador autenticado com `patients.create` |
| **Fluxo principal** | 1. Aceder a "Novo paciente" → 2. Preencher formulário → 3. Sistema valida → 4. Gera nº processo → 5. Grava e audita → 6. Redireciona para ficha |
| **Fluxo alternativo** | 3a. Duplicado detetado → alerta → utilizador confirma ou cancela |
| **Pós-condição** | Paciente ativo na base de dados |

### UC-02 — Pesquisar paciente

| Campo | Valor |
|-------|-------|
| **Ator** | Qualquer perfil com `patients.view` |
| **Fluxo principal** | 1. Introduzir termo de pesquisa → 2. Sistema filtra → 3. Apresenta resultados paginados → 4. Selecionar registo |
| **Extensão** | Filtros por estado (ativo/inativo), género, faixa etária |

### UC-03 — Consultar ficha do paciente

| Campo | Valor |
|-------|-------|
| **Ator** | Médico, Enfermeiro, Rececionista, Laboratório, Financeiro |
| **Pré-condição** | `patients.view` |
| **Fluxo principal** | 1. Abrir ficha → 2. Visualizar dados consolidados → 3. (Opcional) Consultar histórico de auditoria |
| **Restrição** | Dados eliminados (soft) visíveis apenas para Admin |

### UC-04 — Atualizar dados do paciente

| Campo | Valor |
|-------|-------|
| **Ator** | Rececionista, Médico |
| **Pré-condição** | `patients.edit`, paciente ativo |
| **Fluxo principal** | 1. Abrir edição → 2. Alterar campos → 3. Validar → 4. Gravar com auditoria |
| **Exceção** | Documento duplicado → erro 409 |

### UC-05 — Desativar paciente

| Campo | Valor |
|-------|-------|
| **Ator** | Administrador |
| **Pré-condição** | `patients.delete` |
| **Fluxo principal** | 1. Confirmar desativação → 2. Sistema verifica dependências → 3. Soft delete → 4. Auditoria |
| **Fluxo alternativo** | 2a. Dependências ativas → desativação sem eliminação física lógica |

### UC-06 — Exportar listagem de pacientes

| Campo | Valor |
|-------|-------|
| **Ator** | Administrador |
| **Pré-condição** | `patients.export` |
| **Fluxo principal** | 1. Aplicar filtros → 2. Exportar CSV → 3. Download do ficheiro |
| **Nota** | Sprint 4.2 — implementação completa do export |

### UC-07 — Detetar duplicados

| Campo | Valor |
|-------|-------|
| **Ator** | Sistema (automático) |
| **Gatilho** | Submissão do formulário de registo |
| **Fluxo** | Comparar nome + data nascimento + telefone → se match ≥ 80% similaridade → alerta |

---

## 6. User Stories

### Epic: Registo e identificação

| ID | Story | Prioridade |
|----|-------|------------|
| US-01 | Como **rececionista**, quero registar um novo paciente com dados mínimos obrigatórios, para iniciar o atendimento sem demora. | Must |
| US-02 | Como **rececionista**, quero pesquisar pacientes por nome, documento ou telefone, para evitar registos duplicados. | Must |
| US-03 | Como **sistema**, quero gerar automaticamente um número de processo clínico único, para identificar cada utente de forma inequívoca. | Must |
| US-04 | Como **rececionista**, quero ser alertado sobre possíveis duplicados antes de gravar, para manter a base de dados limpa. | Should |

### Epic: Consulta e edição

| ID | Story | Prioridade |
|----|-------|------------|
| US-05 | Como **médico**, quero consultar a ficha resumo de um paciente, para preparar a consulta. | Must |
| US-06 | Como **rececionista**, quero editar dados de contacto de um paciente, para manter a informação atualizada. | Must |
| US-07 | Como **enfermeiro**, quero ver a listagem de pacientes ativos, para localizar utentes no serviço. | Must |
| US-08 | Como **médico**, quero ver o histórico de alterações na ficha, para perceber evolução dos dados. | Could |

### Epic: Governança e segurança

| ID | Story | Prioridade |
|----|-------|------------|
| US-09 | Como **administrador**, quero desativar pacientes que já não frequentam a clínica, para manter listagens relevantes. | Must |
| US-10 | Como **administrador**, quero que todas as alterações fiquem registadas em auditoria, para conformidade e responsabilização. | Must |
| US-11 | Como **administrador**, quero exportar a listagem de pacientes filtrada, para relatórios externos. | Should |
| US-12 | Como **sistema**, quero negar acesso a utilizadores sem permissão `patients.view`, para proteger dados clínicos. | Must |

### Epic: Integração (preparação)

| ID | Story | Prioridade |
|----|-------|------------|
| US-13 | Como **rececionista**, quero ver atalhos na ficha para consultas e exames (desativados até módulos existirem), para fluxo futuro integrado. | Could |
| US-14 | Como **financeiro**, quero consultar dados identificativos do paciente a partir da ficha, para emitir faturas. | Should |

---

## 7. Critérios de Aceitação

### CA-01 — Registo de paciente

```gherkin
Dado que sou rececionista autenticado com permissão patients.create
Quando preencho todos os campos obrigatórios e submeto o formulário
Então o sistema cria o paciente com número de processo único
E retorna HTTP 201 com envelope { success: true, data: { ... } }
E regista auditoria PATIENT_CREATE
```

### CA-02 — Validação de documento duplicado

```gherkin
Dado que existe paciente ativo com document_number "123456789LA045"
Quando tento criar outro paciente com o mesmo document_number
Então o sistema retorna HTTP 409
E a mensagem indica "Já existe um paciente com este documento de identificação"
E nenhum registo é criado
```

### CA-03 — Pesquisa e paginação

```gherkin
Dado que existem 45 pacientes ativos
Quando solicito GET /api/v1/patients/?page=1&search=Silva
Então recebo no máximo 20 resultados
E o envelope data contém { count, next, previous, results }
E cada item inclui id, full_name, phone, is_active, patient_number
```

### CA-04 — RBAC — acesso negado

```gherkin
Dado que sou utilizador sem permissão patients.view
Quando solicito GET /api/v1/patients/
Então recebo HTTP 403
E success é false
```

### CA-05 — Soft delete

```gherkin
Dado que sou administrador com patients.delete
E o paciente ID 42 não tem consultas ativas
Quando solicito DELETE /api/v1/patients/42/
Então o paciente fica com deleted_at preenchido e is_active false
E desaparece da listagem padrão
E regista auditoria PATIENT_DELETE
```

### CA-06 — Edição com auditoria

```gherkin
Dado que sou rececionista com patients.edit
Quando atualizo o telefone do paciente ID 10
Então o campo é atualizado
E auditoria PATIENT_UPDATE regista resource_id=10 e metadata com campos alterados
```

### CA-07 — Frontend listagem

```gherkin
Dado que acedo a /patients com sessão válida e patients.view
Quando a página carrega
Então vejo tabela com colunas: Nº Processo, Nome, Telefone, Estado
E posso pesquisar e navegar entre páginas
```

### CA-08 — Frontend formulário

```gherkin
Dado que acedo a /patients/new
Quando submeto com campos inválidos (ex: telefone curto)
Então vejo mensagens de erro por campo em português
E o formulário não é submetido
```

### CA-09 — Compatibilidade

```gherkin
Dado que os módulos auth e users estão operacionais
Quando implemento o módulo patients
Então todos os testes existentes continuam a passar
E os endpoints /api/v1/auth/* e /api/v1/users/* permanecem inalterados
```

### CA-10 — Menor de idade

```gherkin
Dado que registo paciente com birth_date indicando idade < 18 anos
Quando não preencho dados do responsável legal
Então o sistema rejeita com HTTP 400
E indica campos obrigatórios do responsável
```
