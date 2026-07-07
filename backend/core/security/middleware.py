"""Middleware de cabeçalhos de segurança HTTP."""

from django.conf import settings


class SecurityHeadersMiddleware:
    """Adiciona cabeçalhos de segurança sem alterar contratos da API."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response["X-Content-Type-Options"] = "nosniff"
        response["Referrer-Policy"] = getattr(settings, "SECURE_REFERRER_POLICY", "strict-origin-when-cross-origin")
        if getattr(settings, "SECURE_CONTENT_SECURITY_POLICY", ""):
            response["Content-Security-Policy"] = settings.SECURE_CONTENT_SECURITY_POLICY
        if not settings.DEBUG and getattr(settings, "SECURE_HSTS_SECONDS", 0):
            response["Strict-Transport-Security"] = f"max-age={settings.SECURE_HSTS_SECONDS}; includeSubDomains"
        return response
