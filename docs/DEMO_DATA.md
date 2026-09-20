# Dados de demonstração — SGCS SauVida

## Objectivo

Popular um ambiente de desenvolvimento ou demo com **utilizadores demo por perfil RBAC** e dados clínicos/financeiros fictícios.

## Pré-requisitos

```bash
docker compose up -d
docker exec sgcs-backend python manage.py migrate
docker exec sgcs-backend python manage.py seed_rbac
```

## Comando

Normalmente **não é necessário** — `npm run start` / Docker já executam `seed_demo` no arranque.

Para forçar ou repor palavras-passe:

```bash
npm run seed
# ou
docker compose exec backend python manage.py seed_demo --reset-demo-users
```

Ficheiro: `backend/apps/users/management/commands/seed_demo.py`

## Utilizadores criados

| Perfil | E-mail | Palavra-passe |
|--------|--------|---------------|
| Administrador | `admin@sauvida.gw` | `Demo@2026!` |
| Director | `director@sauvida.gw` | `Demo@2026!` |
| Médico | `medico1@sauvida.gw` | `Demo@2026!` |
| Médico | `medico2@sauvida.gw` | `Demo@2026!` |
| Receção | `rececao@sauvida.gw` | `Demo@2026!` |
| Laboratório | `laboratorio@sauvida.gw` | `Demo@2026!` |
| Enfermagem | `enfermeiro@sauvida.gw` | `Demo@2026!` |

**Não é criado** utilizador com perfil `FINANCEIRO`. Supervisão financeira (read-only) via Director; operações de caixa via Receção.

## Dados gerados

- 6 pacientes fictícios (Guiné-Bissau)
- Serviço de consulta demo (`DEMO-CONS-001`)
- 4 consultas (2 médicos)
- 2 check-ins na fila da receção
- 1 pedido laboratorial (recebido)
- 1 orçamento → fatura → pagamento confirmado → recibo (actor: Receção)
- 1 notificação interna por utilizador (`[Demo] …`)
- **Não cria stock de urgência** — criar manualmente no UAT Enfermagem ou via UI stock

O comando é **idempotente** para utilizizadores e pacientes (por e-mail / nº documento). Consultas e faturação podem ser omitidas se já existirem conflitos.

## Reset demo

```bash
# Repor palavras-passe demo (não apaga dados clínicos)
docker compose exec backend python manage.py seed_demo --reset-demo-users

# Ambiente limpo (destrutivo — só demo/dev):
# 1. docker compose down -v
# 2. docker compose up -d
# 3. migrate + seed_rbac + seed_demo
```

## Demo vs piloto real

| | Ambiente **demo** | Ambiente **piloto real** |
|--|-------------------|--------------------------|
| Dados | Fictícios (`seed_demo`, `DEMO-*`) | Reais / migrados |
| Credenciais | `Demo@2026!` | Pessoais; nunca reutilizar demo |
| `seed_demo` | Permitido | **Proibido** |
| Backup | Opcional para testes | **Obrigatório** (`pg_dump` real) |
## Relação com `seed_rbac`

| Comando | Função |
|---------|--------|
| `seed_rbac` | Módulos, acções e matriz de permissões por perfil |
| `seed_demo` | Utilizadores + dados de negócio para UI/demo |
