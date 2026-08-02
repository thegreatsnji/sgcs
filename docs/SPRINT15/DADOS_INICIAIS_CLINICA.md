# Dados iniciais da clínica

Pasta: **`data/clinic/`**

| Ficheiro | Destino no SGCS |
|----------|-----------------|
| `perfil_clinica.json` | `settings.PerfilClinica` (singleton `pk=1`) |
| `departamentos_sauvida.json` | `settings.Departamento` |
| `catalogo_servicos_sauvida.csv` | `billing.Servico` |

---

## 1. Preencher antes do go-live

### `perfil_clinica.json`

Campos a completar com dados oficiais da visita:

- `nif`, `morada`, `telefone`, `telemovel`
- `horario_funcionamento` (texto para recepção e impressões)
- Logótipo e assinatura: carregar depois via UI **Configurações → Clínica** (ficheiros não versionados em git se sensíveis)

### `departamentos_sauvida.json`

Lista organizacional (receção, lab, futuros módulos). **Não cria** funcionalidade de farmácia/cirurgia — apenas estrutura para settings e relatórios futuros.

### `catalogo_servicos_sauvida.csv`

Substituir coluna `preco` pelos preçários reais recolhidos. Adicionar linhas para cada serviço facturado na clínica.

---

## 2. Comandos

A partir da raiz do projecto, com backend Docker activo:

```bash
# Só perfil + departamentos
docker compose exec backend python manage.py seed_clinic_initial

# Perfil + departamentos + catálogo
docker compose exec backend python manage.py seed_clinic_initial --import-catalog

# Só catálogo
docker compose exec backend python manage.py import_servico_catalog
```

Desenvolvimento local (sem Docker):

```bash
cd backend
python manage.py seed_clinic_initial --import-catalog
```

---

## 3. Ordem recomendada no ambiente piloto

1. `migrate` + `seed_rbac`  
2. Utilizadores reais (ou `seed_demo` apenas em UAT)  
3. `seed_clinic_initial --import-catalog`  
4. Rever em **Faturação → Serviços** e **Configurações → Clínica**  
5. UAT com [USER_TESTING_GUIDE.md](../USER_TESTING_GUIDE.md)

---

## 4. Segurança e versionamento

- Não commitar NIF real ou contactos pessoais se a política da clínica o proibir — usar `.env` ou ficheiro local ignorado pelo git.  
- Versionar o CSV de preços com data no nome (`catalogo_servicos_2026-07.csv`) em anexo interno.

---

Ver [CATALOGO_SERVICOS_PRECOS.md](./CATALOGO_SERVICOS_PRECOS.md) para detalhes do CSV.
