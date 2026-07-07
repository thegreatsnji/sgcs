# Administração do Sistema — SGCS

Manual de administração para gestores e administradores.

## Perfis com acesso

| Perfil | Configurações |
|--------|---------------|
| ADMINISTRADOR | Acesso total |
| DIRECTOR | Visualização e edição (sem backups) |
| Outros | Sem acesso por defeito |

## Permissões RBAC

- `settings.view` — consultar configurações
- `settings.edit` — editar entidades (departamentos, especialidades, etc.)
- `settings.security` — políticas de segurança
- `settings.backup` — backups e restauro
- `settings.system` — dashboard e monitorização
- `settings.email` — configuração SMTP
- `settings.featureflags` — activar/desactivar módulos

## Áreas configuráveis

### Clínica (`/settings/clinic`)

Nome, NIF, morada, contactos, moeda, fuso horário, idioma, horário e rodapé.

### Estrutura organizacional

- **Departamentos** — receção, laboratório, faturação, etc.
- **Especialidades médicas** — integração futura com consultas
- **Consultórios/Salas** — número, departamento, capacidade

### Horários e feriados

- Dias úteis com hora de abertura/encerramento
- Feriados e dias especiais

### Tipos de consulta

Primeira consulta, seguimento, urgência, teleconsulta — duração e preço base.

### Laboratório

Tipos de exames, categorias, valores de referência e tempo médio.

### Faturação

IVA, moeda, séries de numeração, descontos e métodos de pagamento.

### Segurança

Sessão, complexidade de password, expiração, tentativas de login e preparação 2FA.

### E-mail e SMS

SMTP configurável com teste de ligação. SMS preparado sem integração real.

### Feature flags

Activar/desactivar: laboratório, financeiro, receção, relatórios, notificações, portais.

### Backups

Criação manual, histórico e restauro (stubs Celery).

## Auditoria

Todas as alterações geram eventos: `SETTINGS_UPDATED`, `SECURITY_CONFIGURATION`, `BACKUP_CREATED`, `FEATURE_FLAG_UPDATED`, etc.

## Cache

Configurações e dashboard do sistema são cacheados em Redis (TTL 300 segundos).
