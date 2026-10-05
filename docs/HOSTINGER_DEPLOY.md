# Deploy SGCS na Hostinger (VPS + Docker)

Guia para publicar o SGCS com **camadas de segurança activas** (HTTPS, cookies seguros, HSTS, throttling, login guard, registo público desactivado, API docs fechados).

## Pré-requisitos Hostinger

- **VPS** (não alojamento partilhado PHP) — Django + PostgreSQL + Redis.
- Domínio apontado para o IP do VPS (registo A) — ou use o IP público para piloto HTTP.
- SSH activo, Docker + Docker Compose instalados.

**Instalação rápida (script):** [deploy/hostinger/README.md](../deploy/hostinger/README.md) — VPS `148.230.113.108`, `bash deploy/hostinger/vps-install.sh`.

## 1. Segredos e ambiente

```bash
cp .env.production.example .env.production
# Editar: SECRET_KEY, DB_PASSWORD, ALLOWED_HOSTS, CORS/CSRF com https://
```

Gerar `SECRET_KEY`:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

**Nunca** usar `seed_demo` em produção (`SGCS_SEED_DEMO=0`).

## 2. Camadas de segurança (já no código)

| Camada | Comportamento |
|--------|----------------|
| **Settings** | `config.settings.production`: `DEBUG=False`, cookies `Secure`, HSTS, SSL redirect |
| **Proxy** | `SECURE_PROXY_SSL_HEADER` + Nginx `X-Forwarded-Proto` |
| **Auth** | JWT + blacklist, refresh rotation, sessões |
| **Login** | Rate limit DRF + `LoginGuardService` (5 falhas → bloqueio 15 min) |
| **Registo** | `ALLOW_PUBLIC_REGISTRATION=false` — só admin cria utilizadores |
| **API docs** | Swagger/ReDoc só se `ENABLE_API_DOCS=true` |
| **Admin Django** | URL configurável `DJANGO_ADMIN_PATH` (ex.: `sgcs-admin`) |
| **Headers** | CSP, `X-Frame-Options`, `Permissions-Policy`, nosniff |
| **Rede** | Compose prod: PostgreSQL/Redis **sem** portas públicas |
| **Verificação** | `python manage.py check_deploy_security` (`check --deploy`) |

## 3. Build e arranque

```bash
docker compose -f docker-compose.prod.yml --env-file .env.production up -d --build
docker compose -f docker-compose.prod.yml exec backend python manage.py check_deploy_security
docker compose -f docker-compose.prod.yml exec backend python manage.py seed_rbac
docker compose -f docker-compose.prod.yml exec backend python manage.py seed_sauvida_staff --password-file /path/to/pw.txt
```

O backend corre **Gunicorn**; o frontend é build estático servido pelo Nginx (`web`).

## 4. HTTPS (Hostinger)

Opções:

1. **SSL no painel Hostinger** + proxy externo, ou  
2. **Certbot** no VPS com Nginx (adicionar bloco `listen 443 ssl` — ver `deploy/nginx/hostinger-ssl.conf.example` quando existir), ou  
3. **Cloudflare** (Full strict) em frente ao VPS.

Com HTTPS activo, confirme:

- `SECURE_SSL_REDIRECT=true`
- `CORS_ALLOWED_ORIGINS` e `CSRF_TRUSTED_ORIGINS` com `https://`
- Nginx envia `X-Forwarded-Proto: https`

## 5. Pós-deploy

- [ ] `GET /health/` e `/ready/` respondem 200
- [ ] Login com utilizador real (não demo)
- [ ] Impressora térmica 80 mm (`formato_recibo=TERMICO_80`)
- [ ] Backup PostgreSQL agendado (`pg_dump` no host)
- [ ] Firewall: só 22, 80, 443 abertos

## 6. Desenvolvimento local vs produção

| | Dev (`docker-compose.yml`) | Prod (`docker-compose.prod.yml`) |
|--|---------------------------|----------------------------------|
| Settings | `development` | `production` |
| Servidor | runserver | Gunicorn |
| Demo | `seed_demo` opcional | **proibido** |
| DB/Redis | portas expostas | rede interna |

Ver também [Production.md](./Production.md), [VPS_SECURITY_AND_GITHUB.md](./VPS_SECURITY_AND_GITHUB.md) (HTTPS, hardening, repo público) e [SPRINT18_PILOT_DEPLOYMENT_CHECKLIST.md](./SPRINT18_PILOT_DEPLOYMENT_CHECKLIST.md).
