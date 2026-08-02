# Checklist — Ambiente piloto (pré go-live)

Marcar **SIM/NÃO/N/A** e data. Responsável: Administrador + fornecedor TI.

## Infraestrutura

| Item | Verificação | SIM | Data | Notas |
|------|-------------|-----|------|-------|
| VPS / servidor | CPU/RAM/disco adequados ao piloto | | | |
| Domínio | DNS aponta para piloto | | | |
| HTTPS | Certificado válido; redirect HTTP→HTTPS | | | |
| `DEBUG` | `False` em produção/piloto | | | |
| `SECRET_KEY` | Valor único; não no repositório | | | |
| `ALLOWED_HOSTS` | Domínio piloto listado | | | |
| CORS | Origens frontend apenas | | | |
| CSRF | Trusted origins configurados | | | |
| PostgreSQL | Versão suportada; ligação segura | | | |
| Redis | Disponível se Celery/cache activo | | | |
| Celery worker/beat | Tarefas assíncronas (se usadas) | | | |
| Backups | Agendados + teste de restauro ([BACKUP_CATALOGO_SAUVIDA_V1.md](BACKUP_CATALOGO_SAUVIDA_V1.md)) | | | |
| Logs | Rotação; sem passwords em claro | | | |
| Monitorização | Health `/api/health` ou equivalente | | | |
| Armazenamento | MEDIA para documentos; quotas | | | |

## Aplicação e dados

| Item | Verificação | SIM | Data | Notas |
|------|-------------|-----|------|-------|
| Utilizadores | Contas por perfil (recepção, 2 médicos, lab., director, admin) | | | |
| RBAC | Permissões seed alinhadas à clínica | | | |
| Catálogo V1 | 119 serviços; `operacional=1` correcto | | | |
| Exames | 87 alinhados ao catálogo | | | |
| Demo vs real | Dados piloto identificados | | | |

## Clínica / físico

| Item | Verificação | SIM | Data | Notas |
|------|-------------|-----|------|-------|
| Internet | Banda estável na recepção e lab. | | | |
| Wi‑Fi | Portáteis da clínica na rede piloto | | | |
| Impressora | Recibo e resultados testados | | | |
| Energia | UPS em servidor/switch crítico | | | |
| Contingência | [PLANO_CONTINGENCIA_CLINICA.md](PLANO_CONTINGENCIA_CLINICA.md) conhecido | | | |

## Gates técnicos (última execução)

| Gate | OK | Data | Log |
|------|----|------|-----|
| `manage.py check` | SIM | 2026-08-02 | `docs/logs/sprint20_manage_check.txt` |
| `makemigrations --check` | SIM | 2026-08-02 | `docs/logs/sprint20_migrations.txt` |
| `pytest -q --reuse-db` | SIM (315) | 2026-08-02 | `docs/logs/sprint20_pytest.txt` |
| `npm run build` | SIM | 2026-08-02 | `docs/logs/sprint20_build.txt` |
| `npm run lint` | SIM (0 erros) | 2026-08-02 | `docs/logs/sprint20_lint.txt` |

**Aprovação ambiente piloto:** _________________ **Data:** __________
