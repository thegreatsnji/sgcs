"""Modelos de auditoria."""

from django.conf import settings
from django.db import models


class AuditAction(models.TextChoices):
    LOGIN = "LOGIN", "Login"
    LOGOUT = "LOGOUT", "Logout"
    USER_CREATE = "USER_CREATE", "Criação de utilizador"
    USER_UPDATE = "USER_UPDATE", "Edição de utilizador"
    USER_DELETE = "USER_DELETE", "Eliminação de utilizador"
    USER_ACTIVATE = "USER_ACTIVATE", "Ativação de utilizador"
    USER_DEACTIVATE = "USER_DEACTIVATE", "Desativação de utilizador"
    PASSWORD_CHANGE = "PASSWORD_CHANGE", "Alteração de palavra-passe"
    PERMISSION_CHANGE = "PERMISSION_CHANGE", "Mudança de permissões"
    ROLE_CHANGE = "ROLE_CHANGE", "Mudança de perfil"
    GROUP_CREATE = "GROUP_CREATE", "Criação de grupo"
    GROUP_UPDATE = "GROUP_UPDATE", "Edição de grupo"
    GROUP_DELETE = "GROUP_DELETE", "Eliminação de grupo"
    PROFILE_UPDATE = "PROFILE_UPDATE", "Atualização de perfil"
    PATIENT_CREATE = "PATIENT_CREATE", "Criação de paciente"
    PATIENT_UPDATE = "PATIENT_UPDATE", "Edição de paciente"
    PATIENT_DELETE = "PATIENT_DELETE", "Eliminação de paciente"
    PATIENT_ACTIVATE = "PATIENT_ACTIVATE", "Ativação de paciente"
    PATIENT_DEACTIVATE = "PATIENT_DEACTIVATE", "Desativação de paciente"
    PATIENT_EXPORT = "PATIENT_EXPORT", "Exportação de pacientes"
    PATIENT_PRINT = "PATIENT_PRINT", "Impressão de ficha"
    RECEPTION_CHECK_IN = "RECEPTION_CHECK_IN", "Check-in na receção"
    RECEPTION_STATUS_CHANGE = "RECEPTION_STATUS_CHANGE", "Alteração de estado na receção"
    RECEPTION_ASSIGN_DOCTOR = "RECEPTION_ASSIGN_DOCTOR", "Encaminhamento para médico"
    RECEPTION_REFERRAL = "RECEPTION_REFERRAL", "Encaminhamento departamental"
    RECEPTION_CANCEL = "RECEPTION_CANCEL", "Cancelamento na receção"
    APPOINTMENT_CREATE = "APPOINTMENT_CREATE", "Criação de consulta"
    APPOINTMENT_START = "APPOINTMENT_START", "Início de consulta"
    APPOINTMENT_UPDATE = "APPOINTMENT_UPDATE", "Actualização de consulta"
    APPOINTMENT_COMPLETE = "APPOINTMENT_COMPLETE", "Conclusão de consulta"
    APPOINTMENT_CANCEL = "APPOINTMENT_CANCEL", "Cancelamento de consulta"
    CONSULTA_CRIADA = "CONSULTA_CRIADA", "Consulta criada"
    CONSULTA_CONFIRMADA = "CONSULTA_CONFIRMADA", "Consulta confirmada"
    CONSULTA_REAGENDADA = "CONSULTA_REAGENDADA", "Consulta reagendada"
    CONSULTA_INICIADA = "CONSULTA_INICIADA", "Consulta iniciada"
    CONSULTA_CONCLUIDA = "CONSULTA_CONCLUIDA", "Consulta concluída"
    CONSULTA_CANCELADA = "CONSULTA_CANCELADA", "Consulta cancelada"
    CONSULTA_CLINICA_EDITADA = "CONSULTA_CLINICA_EDITADA", "Prontuário clínico editado"
    SINAIS_VITAIS_REGISTADOS = "SINAIS_VITAIS_REGISTADOS", "Sinais vitais registados"
    DIAGNOSTICO_ADICIONADO = "DIAGNOSTICO_ADICIONADO", "Diagnóstico adicionado"
    PEDIDO_LABORATORIO = "PEDIDO_LABORATORIO", "Pedido de laboratório"
    PEDIDO_IMAGIOLOGIA = "PEDIDO_IMAGIOLOGIA", "Pedido de imagiologia"
    SEGUIMENTO_AGENDADO = "SEGUIMENTO_AGENDADO", "Seguimento agendado"
    PEDIDO_LABORATORIO_RECEBIDO = "PEDIDO_LABORATORIO_RECEBIDO", "Pedido laboratorial recebido"
    COLHEITA_REALIZADA = "COLHEITA_REALIZADA", "Colheita realizada"
    EXAME_INICIADO = "EXAME_INICIADO", "Exame iniciado"
    EXAME_CONCLUIDO = "EXAME_CONCLUIDO", "Exame concluído"
    RESULTADO_CRIADO = "RESULTADO_CRIADO", "Resultado laboratorial criado"
    RESULTADO_EDITADO = "RESULTADO_EDITADO", "Resultado laboratorial editado"
    RESULTADO_VALIDADO = "RESULTADO_VALIDADO", "Resultado laboratorial validado"
    RESULTADO_PUBLICADO = "RESULTADO_PUBLICADO", "Resultado laboratorial publicado"
    RESULTADO_DOWNLOAD = "RESULTADO_DOWNLOAD", "Download de resultado"
    ANEXO_RESULTADO = "ANEXO_RESULTADO", "Anexo de resultado"
    ORCAMENTO_CRIADO = "ORCAMENTO_CRIADO", "Orçamento criado"
    ORCAMENTO_APROVADO = "ORCAMENTO_APROVADO", "Orçamento aprovado"
    FACTURA_CRIADA = "FACTURA_CRIADA", "Fatura criada"
    FACTURA_CANCELADA = "FACTURA_CANCELADA", "Fatura cancelada"
    PAGAMENTO_REALIZADO = "PAGAMENTO_REALIZADO", "Pagamento realizado"
    PAGAMENTO_CONFIRMADO = "PAGAMENTO_CONFIRMADO", "Pagamento confirmado"
    RECIBO_EMITIDO = "RECIBO_EMITIDO", "Recibo emitido"
    CAIXA_ABERTA = "CAIXA_ABERTA", "Caixa aberta"
    CAIXA_FECHADA = "CAIXA_FECHADA", "Caixa fechada"
    MOVIMENTO_FINANCEIRO = "MOVIMENTO_FINANCEIRO", "Movimento financeiro"
    DESPESA_CRIADA = "DESPESA_CRIADA", "Despesa criada"
    DESPESA_APROVADA = "DESPESA_APROVADA", "Despesa aprovada"
    DESPESA_PAGA = "DESPESA_PAGA", "Despesa paga"
    RELATORIO_FINANCEIRO = "RELATORIO_FINANCEIRO", "Relatório financeiro"
    REPORT_CREATED = "REPORT_CREATED", "Relatório criado"
    REPORT_EXPORTED = "REPORT_EXPORTED", "Relatório exportado"
    REPORT_DOWNLOADED = "REPORT_DOWNLOADED", "Relatório descarregado"
    DASHBOARD_VIEWED = "DASHBOARD_VIEWED", "Dashboard visualizado"
    SETTINGS_UPDATED = "SETTINGS_UPDATED", "Configurações actualizadas"
    SYSTEM_CONFIGURATION = "SYSTEM_CONFIGURATION", "Configuração do sistema"
    EMAIL_CONFIGURATION = "EMAIL_CONFIGURATION", "Configuração de e-mail"
    SECURITY_CONFIGURATION = "SECURITY_CONFIGURATION", "Configuração de segurança"
    BACKUP_CREATED = "BACKUP_CREATED", "Backup criado"
    BACKUP_RESTORED = "BACKUP_RESTORED", "Backup restaurado"
    FEATURE_FLAG_UPDATED = "FEATURE_FLAG_UPDATED", "Feature flag actualizada"
    PRESCRICAO_CRIADA = "PRESCRICAO_CRIADA", "Prescrição criada"
    PRESCRICAO_EDITADA = "PRESCRICAO_EDITADA", "Prescrição editada"
    TRATAMENTO_CRIADO = "TRATAMENTO_CRIADO", "Tratamento criado"
    TRATAMENTO_CONCLUIDO = "TRATAMENTO_CONCLUIDO", "Tratamento concluído"
    EVOLUCAO_ADICIONADA = "EVOLUCAO_ADICIONADA", "Evolução clínica adicionada"
    ALTA_MEDICA = "ALTA_MEDICA", "Alta médica"
    NOTIFICACAO_CRIADA = "NOTIFICACAO_CRIADA", "Notificação criada"
    NOTIFICACAO_ENVIADA = "NOTIFICACAO_ENVIADA", "Notificação enviada"
    NOTIFICACAO_LIDA = "NOTIFICACAO_LIDA", "Notificação lida"
    EMAIL_ENVIADO = "EMAIL_ENVIADO", "E-mail enviado"
    SMS_ENVIADO = "SMS_ENVIADO", "SMS enviado"
    TEMPLATE_CRIADO = "TEMPLATE_CRIADO", "Template criado"
    TEMPLATE_EDITADO = "TEMPLATE_EDITADO", "Template editado"
    PREFERENCIA_ALTERADA = "PREFERENCIA_ALTERADA", "Preferência alterada"
    SERVICO_PRECO_ALTERADO = "SERVICO_PRECO_ALTERADO", "Preço de serviço alterado"
    REDUCAO_VALOR_SOLICITADA = "REDUCAO_VALOR_SOLICITADA", "Redução de valor solicitada"
    REDUCAO_VALOR_APROVADA = "REDUCAO_VALOR_APROVADA", "Redução de valor aprovada"
    REDUCAO_VALOR_REJEITADA = "REDUCAO_VALOR_REJEITADA", "Redução de valor rejeitada"
    REDUCAO_VALOR_APLICADA = "REDUCAO_VALOR_APLICADA", "Redução de valor aplicada"
    REDUCAO_VALOR_CANCELADA = "REDUCAO_VALOR_CANCELADA", "Redução de valor cancelada"
    TENTATIVA_ALTERAR_PRECO_OFICIAL = "TENTATIVA_ALTERAR_PRECO_OFICIAL", "Tentativa de alterar preço oficial"
    CATALOGO_REAL_IMPORTADO = "CATALOGO_REAL_IMPORTADO", "Catálogo real importado"
    CONFLITO_CATALOGO_RESOLVIDO = "CONFLITO_CATALOGO_RESOLVIDO", "Conflito de catálogo resolvido"
    STOCK_ITEM_CRIADO = "STOCK_ITEM_CRIADO", "Item de stock de urgência criado"
    STOCK_ENTRADA = "STOCK_ENTRADA", "Entrada de stock de urgência"
    STOCK_SAIDA = "STOCK_SAIDA", "Saída de stock de urgência"
    STOCK_AJUSTE = "STOCK_AJUSTE", "Ajuste de stock de urgência"
    STOCK_PERDA_EXPIRACAO = "STOCK_PERDA_EXPIRACAO", "Perda/expiração de stock"
    STOCK_ITEM_DESACTIVADO = "STOCK_ITEM_DESACTIVADO", "Item de stock desactivado"


class AuditLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
        verbose_name="Utilizador",
    )
    action = models.CharField("Ação", max_length=50, choices=AuditAction.choices)
    ip_address = models.GenericIPAddressField("Endereço IP", null=True, blank=True)
    user_agent = models.TextField("User Agent", blank=True)
    description = models.TextField("Descrição")
    resource_type = models.CharField("Tipo de recurso", max_length=100, blank=True)
    resource_id = models.CharField("ID do recurso", max_length=100, blank=True)
    metadata = models.JSONField("Metadados", default=dict, blank=True)
    created_at = models.DateTimeField("Data", auto_now_add=True)

    class Meta:
        verbose_name = "Registo de auditoria"
        verbose_name_plural = "Registos de auditoria"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["action"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["user", "created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.action} — {self.created_at:%d/%m/%Y %H:%M}"
