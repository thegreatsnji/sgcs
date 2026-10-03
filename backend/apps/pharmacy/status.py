from datetime import date, timedelta

from django.conf import settings

from apps.pharmacy.constants import EstadoStockUrgencia


def dias_proxima_validade() -> int:
    return int(getattr(settings, "STOCK_URGENCIA_DIAS_PROXIMA_VALIDADE", 30))


def estado_item(*, quantidade: int, stock_minimo: int, validade=None, hoje: date | None = None) -> str:
    hoje = hoje or date.today()
    if validade and validade < hoje:
        return EstadoStockUrgencia.EXPIRADO
    if quantidade <= 0:
        return EstadoStockUrgencia.SEM_STOCK
    if quantidade <= stock_minimo:
        return EstadoStockUrgencia.STOCK_BAIXO
    if validade and validade <= hoje + timedelta(days=dias_proxima_validade()):
        return EstadoStockUrgencia.PROXIMO_DA_VALIDADE
    return EstadoStockUrgencia.DISPONIVEL
