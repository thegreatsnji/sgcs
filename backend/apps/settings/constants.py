"""Constantes do módulo de configurações."""

CACHE_TTL = 300

CACHE_KEY_CLINIC = "sgcs:settings:clinic"
CACHE_KEY_SYSTEM_DASHBOARD = "sgcs:settings:system_dashboard"
CACHE_KEY_SETTINGS_PREFIX = "sgcs:settings:{key}"

DEFAULT_CURRENCY = "FCFA"
DEFAULT_TIMEZONE = "Africa/Bissau"
DEFAULT_LANGUAGE = "pt-PT"

DIAS_SEMANA = [
    ("SEG", "Segunda-feira"),
    ("TER", "Terça-feira"),
    ("QUA", "Quarta-feira"),
    ("QUI", "Quinta-feira"),
    ("SEX", "Sexta-feira"),
    ("SAB", "Sábado"),
    ("DOM", "Domingo"),
]

DEFAULT_FEATURE_FLAGS = {
    "laboratorio": True,
    "financeiro": True,
    "recepcao": True,
    "relatorios": True,
    "notificacoes": True,
    "portal_paciente": False,
    "portal_medico": False,
}

DEFAULT_SECURITY = {
    "sessao_maxima_minutos": 480,
    "password_min_length": 8,
    "password_require_upper": True,
    "password_require_number": True,
    "password_require_special": False,
    "password_expiry_days": 90,
    "password_history_count": 5,
    "max_login_attempts": 5,
    "lockout_minutes": 30,
    "two_factor_enabled": False,
}

DEFAULT_FILE_SETTINGS = {
    "max_upload_mb": 10,
    "allowed_types": ["pdf", "jpg", "jpeg", "png", "doc", "docx", "xlsx"],
    "storage_backend": "local",
}

DEFAULT_EMAIL = {
    "host": "",
    "port": 587,
    "use_ssl": False,
    "use_tls": True,
    "username": "",
    "password": "",
    "from_email": "",
}

DEFAULT_SMS = {
    "provider": "",
    "api_key": "",
    "sender_id": "",
    "activo": False,
}

DEFAULT_BILLING = {
    "iva_percentagem": 0,
    "moeda": DEFAULT_CURRENCY,
    "serie_faturas": "FAT",
    "serie_recibos": "REC",
    "serie_orcamentos": "ORC",
    "desconto_maximo_percentagem": 20,
    "metodos_pagamento": ["DINHEIRO", "TRANSFERENCIA", "MULTIBANCO", "CARTAO"],
}
