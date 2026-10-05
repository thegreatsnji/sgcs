"""Verificações de segurança para deploy (production / piloto)."""

import os

from django.conf import settings
from django.core.checks import Error, Warning, register


@register(deploy=True)
def check_secret_key(app_configs, **kwargs):
    if settings.DEBUG:
        return []
    key = settings.SECRET_KEY
    issues = []
    insecure_prefixes = ("django-insecure", "altere-esta-chave", "change-me")
    if not key or len(key) < 50:
        issues.append(
            Error(
                "SECRET_KEY demasiado curta ou em falta (mín. ~50 caracteres).",
                id="sgcs.E001",
            )
        )
    elif any(key.lower().startswith(p) for p in insecure_prefixes):
        issues.append(
            Error(
                "SECRET_KEY parece ser o valor de exemplo. Gere uma chave única.",
                id="sgcs.E002",
            )
        )
    return issues


@register(deploy=True)
def check_allowed_hosts(app_configs, **kwargs):
    if settings.DEBUG:
        return []
    hosts = settings.ALLOWED_HOSTS
    if not hosts or hosts == ["localhost", "127.0.0.1", "backend"]:
        return [
            Error(
                "ALLOWED_HOSTS deve incluir o domínio público (ex.: sgcs.seudominio.com).",
                id="sgcs.E003",
            )
        ]
    return []


@register(deploy=True)
def check_cors_csrf_origins(app_configs, **kwargs):
    if settings.DEBUG:
        return []
    issues = []
    if not getattr(settings, "CORS_ALLOWED_ORIGINS", None):
        issues.append(
            Warning(
                "CORS_ALLOWED_ORIGINS vazio — o frontend não conseguirá chamar a API.",
                id="sgcs.W001",
            )
        )
    csrf = getattr(settings, "CSRF_TRUSTED_ORIGINS", [])
    if not csrf:
        issues.append(
            Warning(
                "CSRF_TRUSTED_ORIGINS vazio — recomendado com HTTPS e admin Django.",
                id="sgcs.W002",
            )
        )
    for origin in getattr(settings, "CORS_ALLOWED_ORIGINS", []):
        if origin == "*" or not origin.startswith("https://"):
            issues.append(
                Warning(
                    f"Origem CORS não-HTTPS ou wildcard: {origin!r}",
                    id="sgcs.W003",
                )
            )
    return issues


@register(deploy=True)
def check_ssl_redirect(app_configs, **kwargs):
    if settings.DEBUG:
        return []
    if os.getenv("APP_ENV", "") != "production":
        return []
    if not getattr(settings, "SECURE_SSL_REDIRECT", False):
        return [
            Warning(
                "SECURE_SSL_REDIRECT=false — active true atrás de HTTPS (Hostinger).",
                id="sgcs.W004",
            )
        ]
    return []


@register(deploy=True)
def check_public_registration(app_configs, **kwargs):
    if settings.DEBUG:
        return []
    if getattr(settings, "ALLOW_PUBLIC_REGISTRATION", False):
        return [
            Warning(
                "ALLOW_PUBLIC_REGISTRATION=true — desactive em produção clínica.",
                id="sgcs.W005",
            )
        ]
    return []
