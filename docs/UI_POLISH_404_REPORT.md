# Relatório: polimento de UI e página 404

## Páginas revistas

Login, cabeçalho, rodapé, painéis por perfil, receção, faturação, consultas, pacientes, laboratório, relatórios, notificações, stock de urgência.

## Strings ajustadas

Títulos e frases com travessão de separação; slogan de login; título HTML; rodapé; empty/help texts institucionais.

## Página 404

`NotFoundPage` com `ErrorPage`: código 404, título “Página não encontrada”, mensagem institucional, acções Voltar e Voltar ao início.

Utilizador autenticado: início = painel do perfil (`getRoleDashboardPath`).  
Não autenticado: `/login`.

Rota `*` e `/404` apontam para o mesmo componente. Rotas protegidas e RBAC não foram alterados.

## ErrorBoundary

Texto: “Não foi possível apresentar esta página”. Sem stack trace. Tentar novamente e Voltar ao início.

## Backend 404

Preservado (JSON DRF para APIs). Sem handler HTML Django nesta tarefa.

## Gates

- `npm run lint`: 0 erros (10 avisos pré-existentes)
- `npm run build`: OK
- `python manage.py check`: OK (backend 404 JSON inalterado)
