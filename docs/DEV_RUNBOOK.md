# SGCS — Arranque rápido

## Onde correr cada comando (pastas)

O repositório tem uma **raiz do projeto**. No seu PC costuma ser:

```text
C:\PROJECTS\SGCS
```

Confirme que está na raiz: deve existir `package.json`, `docker-compose.yml` e as pastas `backend\` e `frontend\`.

```powershell
cd C:\PROJECTS\SGCS
```

| O que quer fazer | Pasta (directório) | Exemplo de comando |
|------------------|--------------------|--------------------|
| **Arrancar / parar a app (Docker)** — uso normal para testes | **Raiz** `C:\PROJECTS\SGCS` | `npm run start` · `npm run stop` · `docker compose up -d --build` |
| **Scripts de atalho** | **Raiz** | `.\scripts\start-for-testing.ps1` |
| **Repor passwords demo (Docker)** | **Raiz** | `npm run seed` ou `docker compose exec backend python manage.py seed_demo --reset-demo-users` |
| **Só PostgreSQL + Redis (modo híbrido)** | **Raiz** | `docker compose up -d db redis` |
| **API Django local** (`runserver`) | **`backend\`** | `cd backend` → activar venv → `python manage.py runserver` |
| **Frontend local** (`npm run dev`) | **`frontend\`** | `cd frontend` → `npm run dev` |
| **Testes pytest** | **`backend\`** | `cd backend` → `python -m pytest` |
| **Lint frontend** | **`frontend\`** | `cd frontend` → `npm run lint` |
| **Setup inicial híbrido (Windows)** | **Raiz** | `.\scripts\setup-dev.bat` |

**Regra simples:** se o comando é `npm run …` ou `docker compose …`, está sempre na **raiz**. Só entre em `backend\` ou `frontend\` quando o guia disser explicitamente.

---

## Para testar (recomendado)

**Requisitos:** [Docker Desktop](https://www.docker.com/) + [Node.js](https://nodejs.org/) 20+ (só para o comando `npm` na raiz).

```powershell
cd C:\PROJECTS\SGCS
npm run start
```

Na primeira execução isto cria `.env`, sobe **toda a stack** (PostgreSQL, Redis, API, frontend, Celery), aplica migrações, RBAC e **dados demo** automaticamente.

| O quê | URL |
|--------|-----|
| **Aplicação** | http://localhost:5173 |
| **API (Swagger)** | http://localhost:8000/api/docs/ |

**Login demo:** `admin@sauvida.gw` / `Demo@2026!` — outros perfis em [DEMO_DATA.md](./DEMO_DATA.md).

**Em segundo plano** (liberta o terminal) — ainda na **raiz**:

```powershell
cd C:\PROJECTS\SGCS
npm run start:bg
npm run ready
```

**Parar** — na **raiz**:

```powershell
cd C:\PROJECTS\SGCS
npm run stop
```

Atalhos equivalentes (na **raiz** `C:\PROJECTS\SGCS`):

- Windows: `.\scripts\start-for-testing.ps1`
- Linux/macOS: `./scripts/start-for-testing.sh`

---

## Comandos úteis

Todos na **raiz** `C:\PROJECTS\SGCS` (excepto se indicado noutra secção):

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
| Login falha no Docker (`proxy error` / ECONNREFUSED) | Recriar frontend: `docker compose up -d --build frontend` |
| Frontend sem API (dev local) | `VITE_API_URL=http://localhost:8000` no `.env` |
| Reset total da BD | `docker compose down -v` (apaga volume PostgreSQL) e `npm run start` |

Desactivar seed automático no Docker: `SGCS_SEED_DEMO=0` no `.env`.
