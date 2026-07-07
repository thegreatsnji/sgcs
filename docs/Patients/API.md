# API REST — Módulo de Gestão de Pacientes

**Projeto:** SGCS — Sistema de Gestão Clínica SauVida  
**Base URL:** `/api/v1/patients/`  
**Versão:** 1.0  
**Estado:** Implementado (Sprint 4)

> Referências: [Database.md](./Database.md) · [Especificacao-Funcional.md](./Especificacao-Funcional.md) · Padrão do módulo `users`

---

## Índice

1. [Convenções gerais](#1-convenções-gerais)
2. [Autenticação e autorização](#2-autenticação-e-autorização)
3. [Formato de resposta](#3-formato-de-resposta)
4. [Paginação, filtros, pesquisa e ordenação](#4-paginação-filtros-pesquisa-e-ordenação)
5. [Validações](#5-validações)
6. [Códigos HTTP e erros](#6-códigos-http-e-erros)
7. [Paciente — endpoints principais](#7-paciente--endpoints-principais)
8. [Contactos de emergência](#8-contactos-de-emergência)
9. [Seguros](#9-seguros)
10. [Alergias](#10-alergias)
11. [Doenças crónicas](#11-doenças-crónicas)
12. [Documentos](#12-documentos)
13. [Fotografias](#13-fotografias)
14. [Histórico](#14-histórico)
15. [Observações](#15-observações)
16. [Integrações futuras (stubs)](#16-integrações-futuras-stubs)
17. [Resumo de endpoints](#17-resumo-de-endpoints)

---

## 1. Convenções gerais

| Aspeto | Padrão SGCS |
|--------|-------------|
| Prefixo global | `/api/v1/` |
| Recurso base | `/api/v1/patients/` |
| Autenticação | JWT — header `Authorization: Bearer <access_token>` |
| Content-Type | `application/json` (exceto upload: `multipart/form-data`) |
| Trailing slash | Obrigatória em todos os endpoints |
| Datas na API | `DD/MM/YYYY` |
| Data/hora na API | `DD/MM/YYYY HH:MM` |
| Idioma das mensagens | Português |
| Documentação interativa | Swagger UI em `/api/docs/` |

### Montagem de URLs (planeada)

```python
# config/urls.py
path("api/v1/patients/", include("apps.patients.urls")),

# apps/patients/urls.py
router = DefaultRouter()
router.register("", PatientViewSet, basename="patient")
router.register(
    r"(?P<patient_pk>\d+)/emergency-contacts",
    PatientEmergencyContactViewSet,
    basename="patient-emergency-contact",
)
# ... demais nested routers
```

---

## 2. Autenticação e autorização

### Autenticação

Todos os endpoints requerem JWT válido. Pedidos sem token ou com token expirado recebem `401 Unauthorized`.

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Autorização (RBAC)

Permissões verificadas via `HasModulePermission`. Codenames do módulo `patients`:

| Codename | Descrição |
|----------|-----------|
| `patients.view` | Consultar listagens e fichas |
| `patients.create` | Registar pacientes e recursos associados |
| `patients.edit` | Editar dados existentes |
| `patients.delete` | Desativar / soft delete |
| `patients.export` | Exportar listagens |
| `patients.print` | Imprimir ficha |
| `patients.admin` | Operações administrativas avançadas |

**Bypass:** `superuser` e perfil `ADMINISTRADOR` têm acesso total.

### Matriz resumida por endpoint

| Operação | Permissão mínima |
|----------|------------------|
| `GET` (listagem/detalhe) | `patients.view` |
| `POST` (criar) | `patients.create` |
| `PATCH` / `PUT` | `patients.edit` |
| `DELETE` | `patients.delete` |
| `activate` | `patients.edit` |
| `deactivate` | `patients.delete` |
| `export` | `patients.export` |
| `print` | `patients.print` |
| Recursos aninhados — leitura | `patients.view` |
| Recursos aninhados — escrita | `patients.create` / `patients.edit` |
| Recursos aninhados — remoção | `patients.edit` |

---

## 3. Formato de resposta

### Envelope de sucesso

Padrão definido em `core/responses.success_response`:

```json
{
  "success": true,
  "message": "Operação concluída com sucesso.",
  "data": { }
}
```

### Envelope de erro

Padrão definido em `core/responses.error_response`:

```json
{
  "success": false,
  "message": "Descrição legível do erro.",
  "errors": { }
}
```

### Listagem paginada

O campo `data` contém o objeto paginado (padrão `UserViewSet.list`):

```json
{
  "success": true,
  "message": "Listagem obtida com sucesso.",
  "data": {
    "count": 150,
    "next": "http://localhost:8000/api/v1/patients/?page=2",
    "previous": null,
    "results": [ ]
  }
}
```

### Resposta sem corpo de dados

Algumas ações (ex.: `DELETE`, `deactivate`) podem devolver `data: null`:

```json
{
  "success": true,
  "message": "Paciente eliminado com sucesso.",
  "data": null
}
```

---

## 4. Paginação, filtros, pesquisa e ordenação

### Paginação

Implementada via `StandardPagination` (`core/pagination.py`).

| Parâmetro | Tipo | Default | Máximo | Descrição |
|-----------|------|---------|--------|-----------|
| `page` | integer | `1` | — | Número da página |
| `page_size` | integer | `20` | `100` | Itens por página |

**Exemplo:**

```http
GET /api/v1/patients/?page=2&page_size=50
```

### Pesquisa (`search`)

Pesquisa textual case-insensitive nos campos configurados no ViewSet.

**Pacientes — campos pesquisáveis:**

| Campo | Descrição |
|-------|-----------|
| `full_name` | Nome completo |
| `first_name` | Nome |
| `last_name` | Apelido |
| `document_number` | Documento de identificação |
| `phone` | Telefone |
| `patient_number` | Nº processo clínico |
| `email` | E-mail |

**Exemplo:**

```http
GET /api/v1/patients/?search=Silva
```

### Filtros (`PatientFilter`)

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `is_active` | boolean | `true` / `false` |
| `is_deleted` | boolean | Incluir eliminados (requer `patients.admin`) |
| `gender` | string | `M`, `F`, `O` |
| `document_type` | string | `BI`, `PASSAPORTE`, `CARTAO_RESIDENTE`, `OUTRO` |
| `blood_type` | string | `A+`, `A-`, …, `DESCONHECIDO` |
| `birth_date_after` | date | Nascimento ≥ data (`DD/MM/YYYY`) |
| `birth_date_before` | date | Nascimento ≤ data |
| `created_after` | datetime | Criado após |
| `created_before` | datetime | Criado antes |
| `has_allergies` | boolean | Com alergias ativas |
| `has_chronic_diseases` | boolean | Com doenças crónicas ativas |

**Exemplo combinado:**

```http
GET /api/v1/patients/?search=Mendes&is_active=true&gender=F&ordering=-created_at
```

### Ordenação (`ordering`)

| Parâmetro | Tipo | Default | Descrição |
|-----------|------|---------|-----------|
| `ordering` | string | `last_name,first_name` | Campo(s) de ordenação |

**Campos permitidos:**

`last_name`, `first_name`, `full_name`, `birth_date`, `created_at`, `updated_at`, `patient_number`

**Ordem descendente:** prefixo `-` (ex.: `-created_at`)

**Exemplo:**

```http
GET /api/v1/patients/?ordering=-created_at
```

---

## 5. Validações

### Campos obrigatórios — Paciente (`POST`)

| Campo | Regra |
|-------|-------|
| `first_name` | Não vazio, máx. 100 caracteres |
| `last_name` | Não vazio, máx. 100 caracteres |
| `birth_date` | Obrigatório, formato `DD/MM/YYYY`, não futuro, idade ≤ 120 anos |
| `gender` | Obrigatório: `M`, `F`, `O` |
| `phone` | Obrigatório, padrão `+?[0-9]{7,15}` |

### Campos opcionais com validação

| Campo | Regra |
|-------|-------|
| `document_number` | Único entre pacientes ativos/não eliminados |
| `document_type` | Enum: `BI`, `PASSAPORTE`, `CARTAO_RESIDENTE`, `OUTRO` |
| `email` | Formato e-mail válido; único se preenchido |
| `blood_type` | Enum: `A+`, `A-`, `B+`, `B-`, `AB+`, `AB-`, `O+`, `O-`, `DESCONHECIDO` |
| `marital_status` | Enum: `SOLTEIRO`, `CASADO`, `DIVORCIADO`, `VIUVO`, `OUTRO` |
| `address_*` | Campos escalares opcionais (ver Database.md) |

### Regras de negócio (aplicação)

| ID | Validação | HTTP |
|----|-----------|------|
| RN-02 | Documento duplicado | `409 Conflict` |
| RN-03 | Possível duplicado (nome + nascimento + telefone) | `200` com alerta em `check-duplicate` |
| RN-07 | Menor de 18 anos sem contacto de emergência | `400 Bad Request` |
| RN-09 | Soft delete com dependências ativas | `400 Bad Request` |
| RN-12 | Sem permissão RBAC | `403 Forbidden` |

### Validações — recursos aninhados

| Recurso | Regras principais |
|---------|-------------------|
| Contacto emergência | `name`, `phone`, `relationship` obrigatórios; apenas um `is_primary=true` ativo |
| Seguro | `provider_name`, `policy_number` obrigatórios; `valid_until >= valid_from` |
| Alergia | `allergen`, `severity` obrigatórios; sem duplicado ativo do mesmo alergénio |
| Doença crónica | `disease_name` obrigatório |
| Documento | `title`, `document_type`, ficheiro obrigatórios no upload |
| Fotografia | Ficheiro imagem (`image/jpeg`, `image/png`, `image/webp`); máx. 5 MB |
| Observação | `content` não vazio; `observation_type` enum |

---

## 6. Códigos HTTP e erros

### Códigos utilizados

| Código | Situação |
|--------|----------|
| `200 OK` | Leitura ou atualização bem-sucedida |
| `201 Created` | Recurso criado |
| `400 Bad Request` | Validação falhou ou regra de negócio violada |
| `401 Unauthorized` | Token ausente, inválido ou expirado |
| `403 Forbidden` | Sem permissão RBAC |
| `404 Not Found` | Recurso inexistente ou inacessível |
| `409 Conflict` | Conflito (ex.: documento duplicado) |
| `500 Internal Server Error` | Erro não tratado |

### Erros de validação (`400`)

`errors` contém um objeto com chaves por campo:

```json
{
  "success": false,
  "message": "Dados inválidos.",
  "errors": {
    "phone": ["Introduza um número de telefone válido."],
    "birth_date": ["A data de nascimento não pode ser futura."],
    "emergency_contacts": ["Paciente menor de idade requer pelo menos um contacto de emergência."]
  }
}
```

### Erro de autenticação (`401`)

```json
{
  "success": false,
  "message": "Credenciais de autenticação não fornecidas.",
  "errors": null
}
```

### Erro de permissão (`403`)

```json
{
  "success": false,
  "message": "Não tem permissão para executar esta ação.",
  "errors": {
    "required_permission": "patients.create"
  }
}
```

### Erro não encontrado (`404`)

```json
{
  "success": false,
  "message": "Paciente não encontrado.",
  "errors": null
}
```

### Erro de conflito (`409`)

```json
{
  "success": false,
  "message": "Já existe um paciente com este documento de identificação.",
  "errors": {
    "document_number": ["123456789LA045"],
    "existing_patient_id": 15
  }
}
```

### Erro de regra de negócio (`400`)

```json
{
  "success": false,
  "message": "Não é possível eliminar o paciente: existem consultas ativas.",
  "errors": {
    "dependencies": ["appointments"]
  }
}
```

---

## 7. Paciente — endpoints principais

### 7.1 Listar pacientes

```http
GET /api/v1/patients/
```

| Aspeto | Valor |
|--------|-------|
| **Permissão** | `patients.view` |
| **Paginação** | Sim |
| **Filtros** | Sim (secção 4) |

**Response `200`:**

```json
{
  "success": true,
  "message": "Listagem obtida com sucesso.",
  "data": {
    "count": 2,
    "next": null,
    "previous": null,
    "results": [
      {
        "id": 1,
        "patient_number": "PAC-2026-00001",
        "full_name": "Maria Mendes",
        "first_name": "Maria",
        "last_name": "Mendes",
        "document_number": "123456789LA045",
        "document_type": "BI",
        "phone": "+245955123456",
        "email": "maria.mendes@email.com",
        "birth_date": "15/03/1990",
        "gender": "F",
        "is_active": true,
        "created_at": "03/07/2026 10:30"
      },
      {
        "id": 2,
        "patient_number": "PAC-2026-00002",
        "full_name": "João Silva",
        "first_name": "João",
        "last_name": "Silva",
        "document_number": null,
        "document_type": null,
        "phone": "+245955987654",
        "email": null,
        "birth_date": "22/08/1985",
        "gender": "M",
        "is_active": true,
        "created_at": "03/07/2026 11:15"
      }
    ]
  }
}
```

---

### 7.2 Criar paciente

```http
POST /api/v1/patients/
```

| Aspeto | Valor |
|--------|-------|
| **Permissão** | `patients.create` |
| **Content-Type** | `application/json` |

**Request:**

```json
{
  "first_name": "Maria",
  "last_name": "Mendes",
  "document_type": "BI",
  "document_number": "123456789LA045",
  "birth_date": "15/03/1990",
  "gender": "F",
  "phone": "+245955123456",
  "email": "maria.mendes@email.com",
  "nationality": "Guineense",
  "blood_type": "O+",
  "marital_status": "CASADO",
  "occupation": "Professora",
  "address_street": "Rua da Independência, nº 12",
  "address_city": "Bissau",
  "address_region": "Bissau",
  "address_country": "Guiné-Bissau",
  "address_postal_code": "1000",
  "emergency_contacts": [
    {
      "name": "João Mendes",
      "phone": "+245955654321",
      "relationship": "CONJUGE",
      "is_primary": true
    }
  ]
}
```

**Response `201`:**

```json
{
  "success": true,
  "message": "Paciente registado com sucesso.",
  "data": {
    "id": 1,
    "patient_number": "PAC-2026-00001",
    "first_name": "Maria",
    "last_name": "Mendes",
    "full_name": "Maria Mendes",
    "document_type": "BI",
    "document_number": "123456789LA045",
    "birth_date": "15/03/1990",
    "gender": "F",
    "phone": "+245955123456",
    "email": "maria.mendes@email.com",
    "nationality": "Guineense",
    "blood_type": "O+",
    "marital_status": "CASADO",
    "occupation": "Professora",
    "address_street": "Rua da Independência, nº 12",
    "address_city": "Bissau",
    "address_region": "Bissau",
    "address_country": "Guiné-Bissau",
    "address_postal_code": "1000",
    "is_active": true,
    "is_deleted": false,
    "deleted_at": null,
    "created_at": "03/07/2026 14:30",
    "updated_at": "03/07/2026 14:30",
    "created_by": {
      "id": 3,
      "full_name": "Ana Receção"
    },
    "emergency_contacts": [
      {
        "id": 1,
        "name": "João Mendes",
        "phone": "+245955654321",
        "relationship": "CONJUGE",
        "is_primary": true,
        "is_active": true
      }
    ],
    "allergies_count": 0,
    "chronic_diseases_count": 0,
    "primary_photo_url": null
  }
}
```

---

### 7.3 Obter paciente

```http
GET /api/v1/patients/{id}/
```

| Aspeto | Valor |
|--------|-------|
| **Permissão** | `patients.view` |

**Response `200`:** objeto completo do paciente (como `data` em 7.2), incluindo contagens de recursos associados.

---

### 7.4 Atualizar paciente (parcial)

```http
PATCH /api/v1/patients/{id}/
```

| Aspeto | Valor |
|--------|-------|
| **Permissão** | `patients.edit` |

**Request (exemplo):**

```json
{
  "phone": "+245955111222",
  "email": "maria.nova@email.com",
  "address_city": "Bissau"
}
```

**Response `200`:**

```json
{
  "success": true,
  "message": "Paciente atualizado com sucesso.",
  "data": {
    "id": 1,
    "patient_number": "PAC-2026-00001",
    "full_name": "Maria Mendes",
    "phone": "+245955111222",
    "email": "maria.nova@email.com",
    "updated_at": "03/07/2026 15:00"
  }
}
```

---

### 7.5 Atualizar paciente (completo)

```http
PUT /api/v1/patients/{id}/
```

| Aspeto | Valor |
|--------|-------|
| **Permissão** | `patients.edit` |

Envia todos os campos editáveis. Mesma estrutura de request que `POST` (exceto `patient_number` — read-only).

---

### 7.6 Eliminar paciente (soft delete)

```http
DELETE /api/v1/patients/{id}/
```

| Aspeto | Valor |
|--------|-------|
| **Permissão** | `patients.delete` |

**Response `200`:**

```json
{
  "success": true,
  "message": "Paciente eliminado com sucesso.",
  "data": null
}
```

---

### 7.7 Ativar paciente

```http
POST /api/v1/patients/{id}/activate/
```

| Aspeto | Valor |
|--------|-------|
| **Permissão** | `patients.edit` |
| **Request body** | Vazio |

**Response `200`:**

```json
{
  "success": true,
  "message": "Paciente ativado com sucesso.",
  "data": {
    "id": 1,
    "is_active": true,
    "is_deleted": false,
    "deleted_at": null
  }
}
```

---

### 7.8 Desativar paciente

```http
POST /api/v1/patients/{id}/deactivate/
```

| Aspeto | Valor |
|--------|-------|
| **Permissão** | `patients.delete` |
| **Request body** | Vazio |

**Response `200`:**

```json
{
  "success": true,
  "message": "Paciente desativado com sucesso.",
  "data": {
    "id": 1,
    "is_active": false
  }
}
```

---

### 7.9 Verificar duplicados

```http
GET /api/v1/patients/check-duplicate/
```

| Aspeto | Valor |
|--------|-------|
| **Permissão** | `patients.create` |

**Query parameters:**

| Parâmetro | Obrigatório | Descrição |
|-----------|:-----------:|-----------|
| `first_name` | Sim | Nome |
| `last_name` | Sim | Apelido |
| `birth_date` | Sim | `DD/MM/YYYY` |
| `phone` | Não | Telefone |
| `document_number` | Não | Documento |

**Exemplo:**

```http
GET /api/v1/patients/check-duplicate/?first_name=Maria&last_name=Mendes&birth_date=15/03/1990&phone=+245955123456
```

**Response `200` — sem duplicados:**

```json
{
  "success": true,
  "message": "Nenhum duplicado encontrado.",
  "data": {
    "has_duplicates": false,
    "matches": []
  }
}
```

**Response `200` — com alerta:**

```json
{
  "success": true,
  "message": "Foram encontrados possíveis duplicados.",
  "data": {
    "has_duplicates": true,
    "matches": [
      {
        "id": 5,
        "patient_number": "PAC-2025-00120",
        "full_name": "Maria Mendes",
        "birth_date": "15/03/1990",
        "phone": "+245955123456",
        "similarity_score": 0.92
      }
    ]
  }
}
```

---

### 7.10 Exportar listagem

```http
GET /api/v1/patients/export/
```

| Aspeto | Valor |
|--------|-------|
| **Permissão** | `patients.export` |
| **Sprint** | 4.2 |

**Query parameters:** mesmos filtros da listagem + `format` (`csv` | `xlsx`, default `csv`)

**Response `200` (Sprint 4.1 — stub):**

```json
{
  "success": true,
  "message": "Exportação em desenvolvimento.",
  "data": {
    "formats": ["csv", "xlsx"],
    "ready": false
  }
}
```

**Response `200` (Sprint 4.2 — ficheiro):**

- `Content-Type: text/csv` ou `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
- `Content-Disposition: attachment; filename="pacientes_2026-07-03.csv"`

---

### 7.11 Imprimir ficha

```http
GET /api/v1/patients/{id}/print/
```

| Aspeto | Valor |
|--------|-------|
| **Permissão** | `patients.print` |
| **Sprint** | 4.2 |

**Response `200`:** `application/pdf` — ficha resumo do paciente.

---

### 7.12 Histórico de auditoria do paciente

```http
GET /api/v1/patients/{id}/audit-trail/
```

| Aspeto | Valor |
|--------|-------|
| **Permissão** | `patients.view` |
| **Paginação** | Sim |

**Response `200`:**

```json
{
  "success": true,
  "message": "Histórico de auditoria obtido com sucesso.",
  "data": {
    "count": 3,
    "next": null,
    "previous": null,
    "results": [
      {
        "id": 101,
        "action": "PATIENT_CREATE",
        "description": "Paciente Maria Mendes registado (nº PAC-2026-00001).",
        "user": { "id": 3, "full_name": "Ana Receção" },
        "ip_address": "192.168.1.10",
        "created_at": "03/07/2026 14:30"
      },
      {
        "id": 105,
        "action": "PATIENT_UPDATE",
        "description": "Paciente Maria Mendes atualizado.",
        "user": { "id": 3, "full_name": "Ana Receção" },
        "metadata": { "changed_fields": ["phone", "email"] },
        "created_at": "03/07/2026 15:00"
      }
    ]
  }
}
```

---

## 8. Contactos de emergência

Base: `/api/v1/patients/{patient_id}/emergency-contacts/`

### Listar

```http
GET /api/v1/patients/1/emergency-contacts/
```

**Response `200`:**

```json
{
  "success": true,
  "message": "Listagem obtida com sucesso.",
  "data": {
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
      {
        "id": 1,
        "name": "João Mendes",
        "phone": "+245955654321",
        "email": null,
        "relationship": "CONJUGE",
        "is_primary": true,
        "is_active": true,
        "created_at": "03/07/2026 14:30"
      }
    ]
  }
}
```

### Criar

```http
POST /api/v1/patients/1/emergency-contacts/
```

**Request:**

```json
{
  "name": "Carlos Mendes",
  "phone": "+245955333444",
  "email": "carlos@email.com",
  "relationship": "FILHO",
  "is_primary": false
}
```

**Response `201`:** contacto criado no envelope `data`.

### Obter / Atualizar / Eliminar

```http
GET    /api/v1/patients/1/emergency-contacts/{id}/
PATCH  /api/v1/patients/1/emergency-contacts/{id}/
DELETE /api/v1/patients/1/emergency-contacts/{id}/
```

| Método | Permissão |
|--------|-----------|
| `GET` | `patients.view` |
| `POST` | `patients.create` |
| `PATCH` | `patients.edit` |
| `DELETE` | `patients.edit` (desativa — `is_active=false`) |

---

## 9. Seguros

Base: `/api/v1/patients/{patient_id}/insurances/`

### Criar seguro

```http
POST /api/v1/patients/1/insurances/
```

**Request:**

```json
{
  "provider_name": "SauVida Seguros",
  "policy_number": "POL-2026-88991",
  "plan_type": "COMPLETO",
  "valid_from": "01/01/2026",
  "valid_until": "31/12/2026",
  "is_primary": true,
  "notes": "Cobertura ambulatório e internamento"
}
```

**Response `201`:**

```json
{
  "success": true,
  "message": "Seguro registado com sucesso.",
  "data": {
    "id": 1,
    "provider_name": "SauVida Seguros",
    "policy_number": "POL-2026-88991",
    "plan_type": "COMPLETO",
    "valid_from": "01/01/2026",
    "valid_until": "31/12/2026",
    "is_primary": true,
    "is_active": true,
    "created_at": "03/07/2026 16:00"
  }
}
```

### CRUD completo

| Método | Endpoint |
|--------|----------|
| `GET` | `/api/v1/patients/{patient_id}/insurances/` |
| `POST` | `/api/v1/patients/{patient_id}/insurances/` |
| `GET` | `/api/v1/patients/{patient_id}/insurances/{id}/` |
| `PATCH` | `/api/v1/patients/{patient_id}/insurances/{id}/` |
| `DELETE` | `/api/v1/patients/{patient_id}/insurances/{id}/` |

**Filtros:** `is_active`, `is_primary`, `plan_type`

---

## 10. Alergias

Base: `/api/v1/patients/{patient_id}/allergies/`

### Criar alergia

```http
POST /api/v1/patients/1/allergies/
```

**Request:**

```json
{
  "allergen": "Penicilina",
  "severity": "GRAVE",
  "reaction": "Urticária e edema",
  "diagnosed_at": "10/05/2018",
  "notes": "Evitar betalactâmicos"
}
```

**Response `201`:**

```json
{
  "success": true,
  "message": "Alergia registada com sucesso.",
  "data": {
    "id": 1,
    "allergen": "Penicilina",
    "severity": "GRAVE",
    "reaction": "Urticária e edema",
    "diagnosed_at": "10/05/2018",
    "is_active": true,
    "notes": "Evitar betalactâmicos",
    "recorded_by": { "id": 7, "full_name": "Dr. Paulo Médico" },
    "created_at": "03/07/2026 16:30"
  }
}
```

### CRUD completo

| Método | Endpoint | Permissão escrita |
|--------|----------|-------------------|
| `GET` | `.../allergies/` | — |
| `POST` | `.../allergies/` | `patients.edit` (dado clínico) |
| `PATCH` | `.../allergies/{id}/` | `patients.edit` |
| `DELETE` | `.../allergies/{id}/` | `patients.edit` |

**Enums `severity`:** `LEVE`, `MODERADA`, `GRAVE`, `ANAFILAXIA`

---

## 11. Doenças crónicas

Base: `/api/v1/patients/{patient_id}/chronic-diseases/`

### Criar

```http
POST /api/v1/patients/1/chronic-diseases/
```

**Request:**

```json
{
  "disease_name": "Diabetes mellitus tipo 2",
  "icd_code": "E11",
  "diagnosed_at": "20/01/2020",
  "status": "CONTROLADA",
  "notes": "Em tratamento com metformina"
}
```

**Response `201`:** envelope com `data` do registo criado.

### CRUD completo

| Método | Endpoint |
|--------|----------|
| `GET` | `/api/v1/patients/{patient_id}/chronic-diseases/` |
| `POST` | `/api/v1/patients/{patient_id}/chronic-diseases/` |
| `GET` | `/api/v1/patients/{patient_id}/chronic-diseases/{id}/` |
| `PATCH` | `/api/v1/patients/{patient_id}/chronic-diseases/{id}/` |
| `DELETE` | `/api/v1/patients/{patient_id}/chronic-diseases/{id}/` |

**Enums `status`:** `ATIVA`, `CONTROLADA`, `REMISSAO`, `CURADA`

---

## 12. Documentos

Base: `/api/v1/patients/{patient_id}/documents/`

### Upload de documento

```http
POST /api/v1/patients/1/documents/
Content-Type: multipart/form-data
```

| Campo form | Tipo | Obrigatório |
|------------|------|:-----------:|
| `file` | file | Sim |
| `document_type` | string | Sim |
| `title` | string | Sim |
| `document_number` | string | Não |
| `description` | string | Não |
| `issued_at` | date | Não |
| `expires_at` | date | Não |

**Response `201`:**

```json
{
  "success": true,
  "message": "Documento carregado com sucesso.",
  "data": {
    "id": 1,
    "document_type": "BI",
    "title": "Bilhete de Identidade",
    "document_number": "123456789LA045",
    "file_url": "http://localhost:8000/media/documents/bi_maria_mendes.pdf",
    "mime_type": "application/pdf",
    "size": 245760,
    "issued_at": "01/06/2020",
    "expires_at": "01/06/2030",
    "is_active": true,
    "uploaded_by": { "id": 3, "full_name": "Ana Receção" },
    "created_at": "03/07/2026 17:00"
  }
}
```

### Listar / Obter / Atualizar metadados / Eliminar

| Método | Endpoint | Notas |
|--------|----------|-------|
| `GET` | `.../documents/` | Paginado; filtro `document_type` |
| `GET` | `.../documents/{id}/` | Inclui `file_url` |
| `PATCH` | `.../documents/{id}/` | Apenas metadados (não substitui ficheiro) |
| `DELETE` | `.../documents/{id}/` | `is_active=false` |

**Enums `document_type`:** `BI`, `PASSAPORTE`, `CARTAO_SEGURO`, `CONSENTIMENTO`, `EXAME_EXTERNO`, `DECLARACAO`, `OUTRO`

---

## 13. Fotografias

Base: `/api/v1/patients/{patient_id}/photos/`

### Upload de fotografia

```http
POST /api/v1/patients/1/photos/
Content-Type: multipart/form-data
```

| Campo form | Tipo | Obrigatório |
|------------|------|:-----------:|
| `file` | image | Sim |
| `is_primary` | boolean | Não (default `false`) |
| `caption` | string | Não |
| `taken_at` | datetime | Não |

**Response `201`:**

```json
{
  "success": true,
  "message": "Fotografia carregada com sucesso.",
  "data": {
    "id": 1,
    "file_url": "http://localhost:8000/media/documents/photo_maria.jpg",
    "is_primary": true,
    "caption": "Foto de perfil",
    "taken_at": "03/07/2026 17:15",
    "is_active": true,
    "created_at": "03/07/2026 17:15"
  }
}
```

### Definir foto principal

```http
POST /api/v1/patients/1/photos/{id}/set-primary/
```

| Aspeto | Valor |
|--------|-------|
| **Permissão** | `patients.edit` |
| **Efeito** | Define `is_primary=true` nesta foto; remove flag das restantes |

---

## 14. Histórico

Base: `/api/v1/patients/{patient_id}/history/`

Registo **append-only** — apenas leitura via API pública. Criação automática pelo sistema em mutações.

### Listar histórico

```http
GET /api/v1/patients/1/history/
```

| Aspeto | Valor |
|--------|-------|
| **Permissão** | `patients.view` |
| **Paginação** | Sim |
| **Ordenação default** | `-event_date` |

**Filtros:**

| Parâmetro | Descrição |
|-----------|-----------|
| `event_type` | Tipo de evento |
| `source_module` | Módulo de origem |
| `event_date_after` | Data início |
| `event_date_before` | Data fim |

**Response `200`:**

```json
{
  "success": true,
  "message": "Histórico obtido com sucesso.",
  "data": {
    "count": 2,
    "next": null,
    "previous": null,
    "results": [
      {
        "id": 1,
        "event_type": "REGISTO",
        "title": "Paciente registado",
        "description": "Registo inicial na receção.",
        "event_date": "03/07/2026 14:30",
        "source_module": "patients",
        "source_id": 1,
        "recorded_by": { "id": 3, "full_name": "Ana Receção" },
        "created_at": "03/07/2026 14:30"
      },
      {
        "id": 2,
        "event_type": "ALERGIA",
        "title": "Alergia registada",
        "description": "Penicilina — GRAVE",
        "event_date": "03/07/2026 16:30",
        "source_module": "patients",
        "source_id": 1,
        "metadata": { "allergy_id": 1 },
        "created_at": "03/07/2026 16:30"
      }
    ]
  }
}
```

**Enums `event_type`:** `REGISTO`, `ADMISSAO`, `ALTA`, `CONSULTA`, `EXAME`, `DIAGNOSTICO`, `CIRURGIA`, `MEDICACAO`, `ALERGIA`, `DOENCA_CRONICA`, `DOCUMENTO`, `OBSERVACAO`, `PAGAMENTO`, `OUTRO`

---

## 15. Observações

Base: `/api/v1/patients/{patient_id}/observations/`

### Criar observação

```http
POST /api/v1/patients/1/observations/
```

**Request:**

```json
{
  "observation_type": "CLINICA",
  "content": "Paciente relata cefaleias frequentes nas últimas duas semanas.",
  "is_pinned": false
}
```

**Response `201`:**

```json
{
  "success": true,
  "message": "Observação registada com sucesso.",
  "data": {
    "id": 1,
    "observation_type": "CLINICA",
    "content": "Paciente relata cefaleias frequentes nas últimas duas semanas.",
    "is_pinned": false,
    "is_active": true,
    "created_by": { "id": 7, "full_name": "Dr. Paulo Médico" },
    "created_at": "03/07/2026 18:00",
    "updated_at": "03/07/2026 18:00"
  }
}
```

### CRUD completo

| Método | Endpoint | Permissão |
|--------|----------|-----------|
| `GET` | `.../observations/` | `patients.view` |
| `POST` | `.../observations/` | `patients.edit` |
| `GET` | `.../observations/{id}/` | `patients.view` |
| `PATCH` | `.../observations/{id}/` | `patients.edit` (autor ou admin) |
| `DELETE` | `.../observations/{id}/` | `patients.edit` |

**Filtros:** `observation_type`, `is_pinned`, `is_active`

**Enums `observation_type`:** `CLINICA`, `ENFERMAGEM`, `ADMINISTRATIVA`

### Fixar observação

```http
POST /api/v1/patients/1/observations/{id}/pin/
POST /api/v1/patients/1/observations/{id}/unpin/
```

---

## 16. Integrações futuras (stubs)

Endpoints de agregação read-only na ficha do paciente. Devolvem listas vazias até os módulos downstream existirem.

### Consultas

```http
GET /api/v1/patients/{id}/appointments/
```

**Permissão:** `patients.view` + `appointments.view` (quando disponível)

**Response `200` (stub):**

```json
{
  "success": true,
  "message": "Módulo de consultas em desenvolvimento.",
  "data": {
    "count": 0,
    "next": null,
    "previous": null,
    "results": [],
    "module_ready": false
  }
}
```

### Laboratório

```http
GET /api/v1/patients/{id}/lab-orders/
```

**Permissão:** `patients.view` + `laboratory.view`

### Receitas

```http
GET /api/v1/patients/{id}/prescriptions/
```

**Permissão:** `patients.view` + permissão do módulo de receitas

### Pagamentos

```http
GET /api/v1/patients/{id}/payments/
GET /api/v1/patients/{id}/balance/
```

**Permissão:** `patients.view` + `billing.view`

**Response `200` — saldo (futuro):**

```json
{
  "success": true,
  "message": "Saldo obtido com sucesso.",
  "data": {
    "patient_id": 1,
    "total_invoiced": "150000.00",
    "total_paid": "120000.00",
    "balance": "30000.00",
    "currency": "XOF"
  }
}
```

---

## 17. Resumo de endpoints

### Paciente

| Método | Endpoint | Permissão |
|--------|----------|-----------|
| `GET` | `/api/v1/patients/` | `patients.view` |
| `POST` | `/api/v1/patients/` | `patients.create` |
| `GET` | `/api/v1/patients/{id}/` | `patients.view` |
| `PUT` | `/api/v1/patients/{id}/` | `patients.edit` |
| `PATCH` | `/api/v1/patients/{id}/` | `patients.edit` |
| `DELETE` | `/api/v1/patients/{id}/` | `patients.delete` |
| `POST` | `/api/v1/patients/{id}/activate/` | `patients.edit` |
| `POST` | `/api/v1/patients/{id}/deactivate/` | `patients.delete` |
| `GET` | `/api/v1/patients/check-duplicate/` | `patients.create` |
| `GET` | `/api/v1/patients/export/` | `patients.export` |
| `GET` | `/api/v1/patients/{id}/print/` | `patients.print` |
| `GET` | `/api/v1/patients/{id}/audit-trail/` | `patients.view` |

### Recursos aninhados

| Recurso | Base URL |
|---------|----------|
| Contactos emergência | `/api/v1/patients/{patient_id}/emergency-contacts/` |
| Seguros | `/api/v1/patients/{patient_id}/insurances/` |
| Alergias | `/api/v1/patients/{patient_id}/allergies/` |
| Doenças crónicas | `/api/v1/patients/{patient_id}/chronic-diseases/` |
| Documentos | `/api/v1/patients/{patient_id}/documents/` |
| Fotografias | `/api/v1/patients/{patient_id}/photos/` |
| Histórico | `/api/v1/patients/{patient_id}/history/` (read-only) |
| Observações | `/api/v1/patients/{patient_id}/observations/` |

### Stubs futuros

| Método | Endpoint |
|--------|----------|
| `GET` | `/api/v1/patients/{id}/appointments/` |
| `GET` | `/api/v1/patients/{id}/lab-orders/` |
| `GET` | `/api/v1/patients/{id}/prescriptions/` |
| `GET` | `/api/v1/patients/{id}/payments/` |
| `GET` | `/api/v1/patients/{id}/balance/` |

---

## Referências

- [Modelo de dados](./Database.md)
- [Especificação funcional](./Especificacao-Funcional.md)
- Implementação de referência: `backend/apps/users/views.py`
- Envelope de resposta: `backend/core/responses.py`
- Paginação: `backend/core/pagination.py`
