# Hostinger VPS — SGCS

**Your server (from panel):** `148.230.113.108` · Ubuntu 22.04 · `root@148.230.113.108`

## 1. Open firewall (Hostinger panel)

Allow **TCP 80** (and **443** when you add HTTPS). SSH **22** should already work.

## 2. Connect

From PowerShell on your PC:

```powershell
ssh root@148.230.113.108
```

Use the root password from Hostinger (**Reset password** in the panel if needed).

## 3. One-shot install on the VPS

After SSH login as `root`:

```bash
apt-get update && apt-get install -y git
git clone --depth 1 https://github.com/thegreatsnji/sgcs.git /opt/sgcs
cd /opt/sgcs
bash deploy/hostinger/vps-install.sh
```

Or update an existing clone:

```bash
cd /opt/sgcs && git pull && bash deploy/hostinger/vps-install.sh
```

The script installs Docker if needed, creates `.env.production`, builds `docker-compose.prod.yml`, imports **19 staff** with password **`Demo@2026!`** (override with `STAFF_PASSWORD=...` before running).

## 4. Use the app

- **http://148.230.113.108/** (or your domain later)
- E-mail: `bacar.sanha@sauvida.gw` (or any `@sauvida.gw` from the roster)
- Password: **`Demo@2026!`** until you change it

## 5. Push local changes before install

If you have commits not on GitHub, push first:

```powershell
cd C:\PROJECTS\SGCS
git push origin main
```

Or copy the project to the VPS with `scp`/WinSCP instead of `git clone`.

## 6. Later (when you have a domain + SSL)

Edit `/opt/sgcs/.env.production`:

- Set `ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`, `CSRF_TRUSTED_ORIGINS` to `https://yourdomain`
- Set `INSECURE_HTTP_PILOT=false`, `SECURE_SSL_REDIRECT=true`
- Rebuild: `docker compose -f docker-compose.prod.yml --env-file .env.production up -d --build`

See [docs/HOSTINGER_DEPLOY.md](../../docs/HOSTINGER_DEPLOY.md).
