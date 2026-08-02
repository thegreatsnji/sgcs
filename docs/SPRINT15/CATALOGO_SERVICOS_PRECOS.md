# Catálogo de serviços e preços (FCFA)

**Modelo:** `apps.billing.models.Servico`  
**Ficheiro mestre:** `data/clinic/catalogo_servicos_sauvida.csv`

---

## 1. Objectivo

Centralizar o **preçário real** da clínica num formato importável para faturação (orçamentos, faturas, linhas de serviço), **sem** implementar módulos de farmácia ou cirurgia.

---

## 2. Colunas do CSV

| Coluna | Obrigatório | Descrição |
|--------|:-----------:|-----------|
| `codigo` | Sim | Identificador único (ex.: `CONS-GERAL`, `EX-LAB-HEMO`) |
| `nome` | Sim | Nome apresentado na fatura |
| `descricao` | Não | Detalhe para relatórios |
| `categoria` | Sim | Uma de: `CONSULTA`, `EXAME`, `PROCEDIMENTO`, `INTERNAMENTO`, `OUTRO` |
| `preco` | Sim | Valor em **FCFA** (decimal com ponto) |
| `activo` | Não | `1` / `0` (predefinição: activo) |

### Mapeamento departamento → categoria

| Área na clínica | Categoria `Servico` |
|-----------------|---------------------|
| Consultas | CONSULTA |
| Laboratório / imunologia | EXAME |
| Ecografia, pequenas cirurgias, parto (referência) | EXAME ou PROCEDIMENTO |
| Cirurgia maior, procedimentos | PROCEDIMENTO |
| Diárias / camas | INTERNAMENTO |
| Materiais, taxas farmácia, certificados | OUTRO |

---

## 3. Valores no repositório

O CSV incluído na Sprint 15 é um **modelo de referência** com preços indicativos. **Substituir** cada `preco` pelos valores dos preçários recolhidos na visita presencial antes do go-live.

Manter histórico de alterações (git ou anexo datado) quando a direcção actualizar preços.

---

## 4. Importação

### Validar sem gravar

```bash
docker compose exec backend python manage.py import_servico_catalog --dry-run
```

### Importar para a base de dados

```bash
docker compose exec backend python manage.py import_servico_catalog
```

### Ficheiro alternativo

```bash
docker compose exec backend python manage.py import_servico_catalog --file /caminho/preçario_2026.csv
```

### Desactivar serviços ausentes do ficheiro

```bash
docker compose exec backend python manage.py import_servico_catalog --deactivate-missing
```

---

## 5. Carga completa com perfil clínico

```bash
docker compose exec backend python manage.py seed_clinic_initial --import-catalog
```

Ordem: `perfil_clinica.json` → `departamentos_sauvida.json` → catálogo CSV.

---

## 6. API (alternativa manual)

`GET/POST/PATCH /api/v1/billing/services/` — requer permissões `billing.*`. Preferir importação em massa para o preçário inicial.

---

## 7. Ligação ao laboratório

Tipos de exame em **Configurações → Laboratório** devem ser alinhados com códigos `EX-LAB-*` e preços do CSV para evitar divergência entre pedido clínico e fatura.

---

*Responsável clínico: validar lista final e assinar versão do CSV usada em produção.*
