"""Tarefas Celery do módulo financeiro."""

from config.celery import app


@app.task(name="finance.gerar_relatorio_pdf")
def gerar_relatorio_pdf(tipo: str, periodo: str):
    """Geração de PDF de relatório — implementação futura."""
    return {"status": "ok", "tipo": tipo, "periodo": periodo}


@app.task(name="finance.enviar_relatorio_email")
def enviar_relatorio_email(tipo: str, periodo: str):
    """Envio de relatório por e-mail — implementação futura."""
    return {"status": "ok", "tipo": tipo, "periodo": periodo}


@app.task(name="finance.fechar_caixa")
def fechar_caixa(caixa_id: int):
    """Processamento pós-fecho de caixa — implementação futura."""
    return {"status": "ok", "caixa_id": caixa_id}


@app.task(name="finance.backup_financeiro")
def backup_financeiro():
    """Backup financeiro — implementação futura."""
    return {"status": "ok"}
