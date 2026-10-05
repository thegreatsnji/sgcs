"""Configurações de desenvolvimento."""

from .base import *  # noqa: F403

DEBUG = True

ALLOW_PUBLIC_REGISTRATION = os.getenv("ALLOW_PUBLIC_REGISTRATION", "true").lower() == "true"  # noqa: F405
ENABLE_API_DOCS = os.getenv("ENABLE_API_DOCS", "true").lower() == "true"  # noqa: F405

INSTALLED_APPS += ["debug_toolbar"]  # noqa: F405

MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")  # noqa: F405

INTERNAL_IPS = ["127.0.0.1", "localhost"]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
