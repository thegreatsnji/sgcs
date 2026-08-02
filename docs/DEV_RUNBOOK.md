# SGCS — Arranque rápido

## Para testar (recomendado)

**Requisitos:** [Docker Desktop](https://www.docker.com/) + [Node.js](https://nodejs.org/) 20+ (só para o comando `npm` na raiz).

Na pasta do projeto:

```bash
npm run start
```

Na primeira execução isto cria `.env`, sobe **toda a stack** (PostgreSQL, Redis, API, frontend, Celery), aplica migrações, RBAC e **dados demo** automaticamente.

| O quê | URL |
|--------|-----|
| **Aplicação** | http://localhost:5173 |
| **API (Swagger)** | http://localhost:8000/api/docs/ |

**Login demo:** `admin@sauvida.gw` / `Demo@2026!` — outros perfis em [DEMO_DATA.md](./DEMO_DATA.md).

**Em segundo plano** (liberta o terminal):

```bash
npm run start:bg
npm run ready    # opcional: espera o backend
```

**Parar:**

```bash
npm run stop
```

Atalhos equivalentes:

- Windows: `.\scripts\start-for-testing.ps1`
- Linux/macOS: `./scripts/start-for-testing.sh`

---

## Comandos úteis

| Comando | Função |
|---------|--------|
| `npm run logs` | Ver logs de todos os serviços |
| `npm run down` | Parar e remover contentores (mantém dados na BD) |
| `npm run seed` | Repor palavras-passe dos utilizadores demo |

---

## Desenvolvimento com hot reload (opcional)

Só se estiver a alterar código com frequência:

1. `docker compose up -d db redis`
2. Terminal A: `cd backend` → venv → `python manage.py runserver`
3. Terminal B: `cd frontend` → `npm run dev`

`.env` no host: `DB_HOST=localhost`, Redis em `localhost:6379`.

**Não** correr o backend Docker e `runserver` local ao mesmo tempo (porta 8000).

Setup inicial do modo híbrido: `scripts/setup-dev.bat` (Windows) ou `scripts/setup-dev.sh`.

---

## Testes automatizados

```bash
cd backend && python -m pytest
cd frontend && npm run lint
```

Cenários manuais por perfil: [USER_TESTING_GUIDE.md](./USER_TESTING_GUIDE.md).

---

## Problemas frequentes

| Problema | Solução |
|----------|---------|
| Porta 8000 ocupada | `docker compose stop backend` ou fechar `runserver` local |
| Login falha | `npm run seed` ou `docker compose exec backend python manage.py seed_demo` |
| Frontend sem API | Confirmar `VITE_API_URL=http://localhost:8000` no `.env` |
| Reset total da BD | `docker compose down -v` (apaga volume PostgreSQL) e `npm run start` |

Desactivar seed automático no Docker: `SGCS_SEED_DEMO=0` no `.env`.
