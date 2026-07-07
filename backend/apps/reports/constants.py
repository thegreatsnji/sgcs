"""Constantes do módulo de relatórios."""

CACHE_TTL = 120

CACHE_KEY_REPORT = "sgcs:reports:{tipo}:{periodo}:{filtros_hash}"
CACHE_KEY_EXECUTIVE = "sgcs:reports:executive"
CACHE_KEY_STATISTICS = "sgcs:reports:statistics:{tipo}"
CACHE_KEY_CHARTS = "sgcs:reports:charts:{serie}"

EXPORT_PDF = "pdf"
EXPORT_XLSX = "xlsx"
EXPORT_CSV = "csv"
EXPORT_FORMATS = (EXPORT_PDF, EXPORT_XLSX, EXPORT_CSV)


class ReportPeriod:
    HOJE = "hoje"
    SEMANA = "semana"
    MES = "mes"
    ANO = "ano"
    PERSONALIZADO = "personalizado"

    CHOICES = (HOJE, SEMANA, MES, ANO, PERSONALIZADO)


class ReportType:
    PATIENTS = "patients"
    APPOINTMENTS = "appointments"
    RECEPTION = "reception"
    LABORATORY = "laboratory"
    BILLING = "billing"
    FINANCE = "finance"
    EXECUTIVE = "executive"
