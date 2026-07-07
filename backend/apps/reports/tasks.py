"""Tarefas Celery do módulo de relatórios (stubs)."""

from config.celery import app


@app.task(name="reports.gerar_pdf")
def gerar_pdf(tipo: str, periodo: str) -> dict:
    return {"status": "stub", "tipo": tipo, "periodo": periodo, "formato": "pdf"}


@app.task(name="reports.gerar_excel")
def gerar_excel(tipo: str, periodo: str) -> dict:
    return {"status": "stub", "tipo": tipo, "periodo": periodo, "formato": "xlsx"}


@app.task(name="reports.gerar_csv")
def gerar_csv(tipo: str, periodo: str) -> dict:
    return {"status": "stub", "tipo": tipo, "periodo": periodo, "formato": "csv"}


@app.task(name="reports.enviar_relatorio")
def enviar_relatorio(tipo: str, formato: str) -> dict:
    return {"status": "stub", "tipo": tipo, "formato": formato}


@app.task(name="reports.recalcular_estatisticas")
def recalcular_estatisticas() -> dict:
    from apps.reports.services.cache_service import ReportsCacheService

    ReportsCacheService.invalidate_all()
    return {"status": "stub", "action": "recalcular_estatisticas"}
