"""Configurações de produção."""

import os

from .base import *  # noqa: F403

DEBUG = False

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = int(os.getenv("SECURE_HSTS_SECONDS", "31536000"))
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_SSL_REDIRECT = os.getenv("SECURE_SSL_REDIRECT", "false").lower() == "true"
SESSION_COOKIE_AGE = int(os.getenv("SESSION_COOKIE_AGE", str(60 * 60 * 8)))
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

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
