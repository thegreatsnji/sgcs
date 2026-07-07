"""Tarefas Celery do módulo médico (stubs)."""

from config.celery import app


@app.task(name="doctors.enviar_prescricao_email")
def enviar_prescricao_email(prescricao_id: int) -> dict:
    return {"status": "stub", "prescricao_id": prescricao_id}


@app.task(name="doctors.lembrar_seguimento")
def lembrar_seguimento(seguimento_id: int) -> dict:
    return {"status": "stub", "seguimento_id": seguimento_id}


@app.task(name="doctors.gerar_relatorio_alta")
def gerar_relatorio_alta(alta_id: int) -> dict:
    return {"status": "stub", "alta_id": alta_id}
