# Farmácia de urgência — SGCS

Âmbito **limitado**: stock de medicamentos para **casos urgentes** na clínica. Não é farmácia comercial, não gere receitas ambulatórias completas nem inventário geral.

## Departamento

- Código **FARM** — «Farmácia de Urgência» em `departamentos_sauvida.json` (11.º departamento).

## Funcionalidades

| Funcionalidade | Descrição |
|----------------|-----------|
| Medicamentos | Lista com stock actual e mínimo |
| Movimentos | Entrada, saída (urgência), ajuste (via API) |
| Alertas | Filtro «abaixo do mínimo» |
| Catálogo | Ligação opcional a `Servico` (categoria `MED_URGENCIA`) |

## API

- `GET/POST/PATCH /api/v1/pharmacy/urgent-medicines/`
- `POST /api/v1/pharmacy/urgent-medicines/{id}/movimento/` — body: `{ "tipo": "ENTRADA"|"SAIDA"|"AJUSTE", "quantidade": N, "motivo": "" }`
- `GET /api/v1/pharmacy/urgent-movements/`

## Permissões (RBAC)

| Perfil | Permissões |
|--------|------------|
| Administrador | Todas |
| Enfermeiro | `pharmacy.view`, `pharmacy.edit`, `pharmacy.create` |
| Médico / Director | `pharmacy.view` (consulta) |
| Recepção | Sem acesso por defeito |

Após deploy: `python manage.py seed_rbac`

## UI

- `/pharmacy/urgent-stock` — menu **Farmácia de urgência**

## Comandos

```bash
# Criar registos a partir dos serviços MED_URGENCIA do catálogo
python manage.py sync_pharmacy_urgent_from_catalog

# Departamento FARM (com outros departamentos)
python manage.py seed_clinic_initial
```

## Próximos passos (opcional, fora do âmbito actual)

- Ligar saída de stock a administração na consulta
- Lotes e validades
- Relatório de consumo por período
