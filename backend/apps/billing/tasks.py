"""Tarefas Celery do módulo de faturação."""

from config.celery import app


@app.task(name="billing.emitir_recibo_pdf")
def emitir_recibo_pdf(recibo_id: int):
    """Geração de PDF do recibo — implementação futura."""
    return {"status": "ok", "recibo_id": recibo_id}


@app.task(name="billing.enviar_recibo_email")
def enviar_recibo_email(recibo_id: int):
    """Envio de recibo por e-mail — implementação futura."""
    return {"status": "ok", "recibo_id": recibo_id}


@app.task(name="billing.actualizar_dashboard_financeiro")
def actualizar_dashboard_financeiro():
    """Actualiza cache do dashboard financeiro."""
    from apps.billing.services.cache_service import BillingCacheService

    BillingCacheService.invalidate_all()
    return {"status": "ok"}
