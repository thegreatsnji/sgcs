"""Tarefas Celery do módulo de laboratório."""

from config.celery import app


@app.task(name="laboratory.notify_pending_orders")
def notify_pending_orders():
    """Notificação de pedidos pendentes — implementação futura."""
    return {"status": "ok"}


@app.task(name="laboratory.publicar_resultado")
def publicar_resultado_async(resultado_id: int):
    """Publicação assíncrona de resultado — preparado para notificações externas."""
    return {"status": "ok", "resultado_id": resultado_id}


@app.task(name="laboratory.actualizar_dashboard")
def actualizar_dashboard():
    """Actualiza indicadores do dashboard após validação de resultados."""
    from apps.laboratory.services.cache_service import LaboratoryCacheService

    LaboratoryCacheService.invalidate_all()
    return {"status": "ok"}


@app.task(name="laboratory.notificar_medico")
def notificar_medico(resultado_id: int):
    """Notifica o médico solicitante de que o resultado foi validado."""
    from apps.laboratory.services.result_notification import (
        notify_ordering_doctor_result_validated,
    )

    return notify_ordering_doctor_result_validated(resultado_id)


@app.task(name="laboratory.actualizar_prontuario")
def actualizar_prontuario(resultado_id: int):
    """Sincroniza prontuário clínico após validação — preparado para integrações."""
    from apps.laboratory.models import ResultadoLaboratorial
    from apps.laboratory.services.cache_service import LaboratoryCacheService

    try:
        resultado = ResultadoLaboratorial.objects.select_related("pedido_laboratorial").get(pk=resultado_id)
        pedido = resultado.pedido_laboratorial
        LaboratoryCacheService.invalidate_all(patient_id=pedido.paciente_id, consulta_id=pedido.consulta_id)
    except ResultadoLaboratorial.DoesNotExist:
        return {"status": "not_found", "resultado_id": resultado_id}
    return {"status": "ok", "resultado_id": resultado_id}
