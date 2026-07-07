# Segurança — SGCS

## Rate limiting

- DRF throttling: `anon` 200/h, `user` 5000/h (configurável via env)
- Login: `20/minute` — `LoginRateThrottle`

## Brute-force

`LoginGuardService` — bloqueio após 5 tentativas falhadas (15 min).

## Cabeçalhos HTTP

Middleware `SecurityHeadersMiddleware`:

- `X-Content-Type-Options: nosniff`
- `Referrer-Policy`
- `Content-Security-Policy` (produção)
- `Strict-Transport-Security` (produção)

## Cookies e sessão

- `HttpOnly`, `SameSite=Lax`
- `Secure` em produção

## Uploads

`core/security/upload_validators.py` — limite 10 MB, whitelist MIME.

## Palavras-passe

Mínimo 10 caracteres + validadores Django padrão.

## Logging de segurança

`logs/security.log` quando `LOG_TO_FILES=true`.
