# VPS — concluir configuração, segurança e repositório GitHub

Guia para depois do `vps-install.sh`: hardening, HTTPS com `clinicasauvida.gw`, backups, e **público vs privado** no GitHub.

## 1. No VPS agora (piloto HTTP)

Ligue por SSH e corra:

```bash
cd /opt/sgcs
git pull   # se tiver commits novos no GitHub
bash deploy/hostinger/vps-finish-security.sh
```

Isto verifica permissões de `.env.production`, portas Docker, `check_deploy_security`, e `/health/`.

### Firewall (painel Hostinger)

Regra **`sgcs-web`** (ou equivalente):

| Acção | Protocolo | Porta |
|--------|-----------|-------|
| Accept | TCP | 22 |
| Accept | TCP | 80 |
| Accept | TCP | 443 |
| Drop | Any | any |

PostgreSQL e Redis **não** devem aparecer expostos no `docker ps` (só rede interna).

### Palavras-passe (crítico)

O instalador importa a equipa com a palavra-passe piloto (`Demo@2026!` por defeito). **Qualquer pessoa que a saiba pode entrar** enquanto não a alterar.

1. Entrar como administrador → **Administração → Utilizadores**
2. Alterar palavra-passe de **cada** utilizador real (ou forçar “alterar no primeiro login” quando existir)
3. Desactivar contas que não forem usadas

### SSH

- Criar utilizador `deploy` com chave SSH (recomendado) e reduzir login por palavra-passe root
- Quando a chave funcionar: `PermitRootLogin prohibit-password` em `/etc/ssh/sshd_config`
- Opcional: `apt install fail2ban` para sshd

## 2. HTTPS quando `clinicasauvida.gw` apontar para o VPS

No painel DNS, registo **A** `@` (e `www` se quiser) → IP do VPS. Espere propagação (minutos a horas).

No VPS:

```bash
cd /opt/sgcs
export DOMAIN=clinicasauvida.gw
export CERTBOT_EMAIL=seu-email@clinicasauvida.gw
# opcional, se ainda aceder pelo IP:
# export VPS_IP=148.230.113.108
bash deploy/hostinger/vps-enable-https.sh
```

Abrir **https://clinicasauvida.gw/login** — o browser deve mostrar cadeado válido.

Renovação Let's Encrypt (cron diário, exemplo):

```bash
echo '0 3 * * * root certbot renew --quiet --deploy-hook "cd /opt/sgcs && docker compose -f docker-compose.prod.yml --env-file .env.production up -d web"' >> /etc/cron.d/sgcs-certbot
```

## 3. Backup PostgreSQL

No VPS (ajuste caminho):

```bash
cd /opt/sgcs
mkdir -p /var/backups/sgcs
docker compose -f docker-compose.prod.yml --env-file .env.production exec -T db \
  pg_dump -U sgcs sgcs | gzip > "/var/backups/sgcs/sgcs-$(date +%F).sql.gz"
```

Copie ficheiros `.sql.gz` para fora do VPS (PC, Google Drive encriptado, etc.). **Não** commitar backups no Git.

## 4. O que o código já faz em produção

| Item | Estado |
|------|--------|
| `DEBUG=false`, Gunicorn | Sim |
| JWT + throttling + login guard | Sim |
| Registo público desligado | `ALLOW_PUBLIC_REGISTRATION=false` |
| Swagger/ReDoc | `ENABLE_API_DOCS=false` |
| Admin Django | URL `DJANGO_ADMIN_PATH=sgcs-admin` |
| DB/Redis sem portas públicas | `docker-compose.prod.yml` |
| Cookies seguros + HSTS | Com `INSECURE_HTTP_PILOT=false` + HTTPS |

Comando de verificação:

```bash
docker compose -f docker-compose.prod.yml --env-file .env.production exec backend python manage.py check_deploy_security
```

## 5. GitHub: pode ser **público**?

### Segredos de produção — OK se não commitados

Estes **não** devem estar no Git (e estão no `.gitignore`):

- `.env.production` (`SECRET_KEY`, `DB_PASSWORD`)
- `backend/data/private/` (CSV/JSON real, `pilot_initial_password.txt`)
- Certificados TLS, backups, dados de pacientes

Se nunca commitou `.env.production`, **não há password da base de dados no GitHub**.

### Dados pessoais da equipa — **NÃO** adequado para repo público

Ficheiros **actualmente versionados** com nomes, telemóveis e e-mails reais da clínica:

- `backend/data/clinic/sauvida_staff.csv`
- `backend/data/clinic/sauvida_staff.example.json` (contém os mesmos dados reais, não fictícios)

Publicar o repositório expõe **PII** (RGPD / privacidade dos colaboradores) e facilita phishing (“sabemos o vosso e-mail @sauvida.gw”).

Também documentado no repo:

- IP do VPS e palavra-passe piloto **de demonstração** (`Demo@2026!`) — risco se ainda a usarem em produção, não por estar no README.

### Recomendação

| Opção | Quando usar |
|--------|-------------|
| **Manter repo PRIVADO** | **Recomendado agora** — piloto clínico com roster real |
| Tornar público depois | Só após: (1) remover PII dos ficheiros tracked, (2) usar exemplos fictícios, (3) limpar histórico Git (`git filter-repo` / GitHub secret scanning), (4) palavras-passe de produção únicas e rotacionadas |

Tornar público **sem** limpar histórico deixa CSV/JSON antigos acessíveis para sempre nos commits.

### Checklist rápida “safe to go public”

- [ ] Nenhum `.env.production` ou ficheiro em `backend/data/private/` no histórico Git
- [ ] Roster real só no VPS (`/opt/sgcs/backend/data/private/`), não no GitHub
- [ ] `sauvida_staff.example.json` com dados **fictícios**
- [ ] Palavra-passe piloto **não** usada por utilizadores reais em produção
- [ ] Sem API keys, PEM, ou dumps de BD no repo

## 6. Actualizar o VPS após `git push`

```bash
cd /opt/sgcs
git pull
bash deploy/hostinger/compose-prod.sh up -d --build
bash deploy/hostinger/vps-finish-security.sh
```

Ver também [HOSTINGER_DEPLOY.md](./HOSTINGER_DEPLOY.md) e [deploy/hostinger/README.md](../deploy/hostinger/README.md).
