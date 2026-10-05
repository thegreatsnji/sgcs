"""Configurações de produção."""

import os

from .base import *  # noqa: F403

DEBUG = False

DATABASES["default"]["CONN_MAX_AGE"] = int(os.getenv("DB_CONN_MAX_AGE", "120"))  # noqa: F405

ALLOW_PUBLIC_REGISTRATION = False
ENABLE_API_DOCS = os.getenv("ENABLE_API_DOCS", "false").lower() == "true"

# IP / HTTP piloto no VPS (sem HTTPS ainda). Remover quando tiver certificado.
_INSECURE_HTTP_PILOT = os.getenv("INSECURE_HTTP_PILOT", "false").lower() == "true"

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SESSION_COOKIE_SECURE = not _INSECURE_HTTP_PILOT
CSRF_COOKIE_SECURE = not _INSECURE_HTTP_PILOT
SECURE_HSTS_SECONDS = 0 if _INSECURE_HTTP_PILOT else int(os.getenv("SECURE_HSTS_SECONDS", "31536000"))
SECURE_HSTS_INCLUDE_SUBDOMAINS = os.getenv("SECURE_HSTS_INCLUDE_SUBDOMAINS", "true").lower() == "true"
SECURE_HSTS_PRELOAD = os.getenv("SECURE_HSTS_PRELOAD", "false").lower() == "true"
SECURE_SSL_REDIRECT = (
    False
    if _INSECURE_HTTP_PILOT
    else os.getenv("SECURE_SSL_REDIRECT", "true").lower() == "true"
)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = os.getenv("USE_X_FORWARDED_HOST", "true").lower() == "true"
SESSION_COOKIE_AGE = int(os.getenv("SESSION_COOKIE_AGE", str(60 * 60 * 8)))
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

AUTH_PASSWORD_VALIDATORS = [
    *AUTH_PASSWORD_VALIDATORS,  # noqa: F405
]
AUTH_PASSWORD_VALIDATORS[1] = {
    "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    "OPTIONS": {"min_length": int(os.getenv("PASSWORD_MIN_LENGTH", "10"))},
}

SECURE_CONTENT_SECURITY_POLICY = os.getenv(
    "CSP_HEADER",
    "default-src 'self'; frame-ancestors 'none'; base-uri 'self'",
)

LOG_TO_FILES = os.getenv("LOG_TO_FILES", "true")

if LOG_TO_FILES:
    from core.logging_config import build_logging_config

    LOGGING = build_logging_config(
        BASE_DIR,  # noqa: F405
        json_format=os.getenv("LOG_JSON", "true").lower() == "true",
    )
