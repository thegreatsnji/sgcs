# Sprint 18 — Checklist de implantação piloto

## Segurança

- [ ] `DEBUG=False` no ambiente piloto externo
- [ ] `SECRET_KEY` única e segura
- [ ] `ALLOWED_HOSTS` restrito
- [ ] `CSRF_TRUSTED_ORIGINS` / CORS alinhados ao domínio
- [ ] HTTPS activo

## Infraestrutura

- [ ] PostgreSQL com backups (`backups/pre_sprint18/` + rotina)
- [ ] Redis e Celery (se notificações assíncronas)
- [ ] Health checks `/health`, `/ready`
- [ ] Logs centralizados

## Dados

- [ ] Catálogo materializado (`import_catalogo_sauvida --materialize-without-price`)
- [ ] Preços confirmados importados (CSV validado)
- [ ] Laboratório alinhado (`align_lab_services --apply`)
- [ ] Médicos com `MedicoPerfil` completo
- [ ] Dados demo identificados ou removidos

## Operação

- [ ] Utilizadores e RBAC (`seed_rbac` / produção)
- [ ] Impressora e navegador testados
- [ ] Plano de contingência (restauro SQL documentado)
- [ ] Contacto administrador SauVida

## Pós-go-live

- [ ] UAT receção presencial
- [ ] Registo de issues em `SPRINT18_ISSUES.md`
