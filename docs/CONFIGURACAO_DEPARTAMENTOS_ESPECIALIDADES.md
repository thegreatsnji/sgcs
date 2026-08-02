# Departamentos e especialidades

## Departamentos (`backend/data/departamentos_sauvida.json`)

Administração, Direção, Receção, Consulta Geral, Especialidades Médicas, Enfermagem, Laboratório, Ecografia, Maternidade e Parteira, Cirurgia.

**Não incluídos:** Internamento, Farmácia comercial, Caixa.

Campos API: `codigo`, `nome`, `descricao`, `activo`, `ordem`, `responsavel`, `localizacao`, `horario`, `contactos_internos`.

## Especialidades (`backend/data/especialidades_sauvida.csv`)

- Clínica Geral (`CLIN-GER`)
- Ginecologia (`GIN`)
- Obstetrícia (`OBS`)
- Cirurgia Geral (`CIR-GER`)

Preço de consulta: definir no **Serviço** associado, não na especialidade.

## Endpoints

`/api/v1/settings/departments/`, `/api/v1/settings/specialties/` (existentes).
