"""Modelos RBAC e gestão de utilizadores."""

from django.conf import settings
from django.db import models


class PermissionAction(models.TextChoices):
    VIEW = "view", "Visualizar"
    CREATE = "create", "Criar"
    EDIT = "edit", "Editar"
    DELETE = "delete", "Eliminar"
    EXPORT = "export", "Exportar"
    PRINT = "print", "Imprimir"
    ADMIN = "admin", "Administrar"
    CONFIRM = "confirm", "Confirmar"
    START = "start", "Iniciar"
    FINISH = "finish", "Concluir"
    CANCEL = "cancel", "Cancelar"
    CLINICAL = "clinical", "Prontuário clínico"
    DIAGNOSIS = "diagnosis", "Diagnósticos"
    REQUEST_LAB = "request_lab", "Pedidos laboratório"
    REQUEST_IMAGING = "request_imaging", "Pedidos imagiologia"
    FOLLOWUP = "followup", "Seguimento"
    RECEIVE = "receive", "Receber"
    COLLECT = "collect", "Colheita"
    PROCESS = "process", "Processar"
    RESULTS_VIEW = "results.view", "Ver resultados"
    RESULTS_CREATE = "results.create", "Criar resultados"
    RESULTS_EDIT = "results.edit", "Editar resultados"
    RESULTS_VALIDATE = "results.validate", "Validar resultados"
    RESULTS_PUBLISH = "results.publish", "Publicar resultados"
    RESULTS_DOWNLOAD = "results.download", "Descarregar resultados"
    PAYMENT = "payment", "Pagamentos"
    RECEIPT = "receipt", "Recibos"
    QUOTE = "quote", "Orçamentos"
    CASH = "cash", "Caixa"
    EXPENSE = "expense", "Despesas"
    REPORT = "report", "Relatórios"
    FIN_DASHBOARD = "dashboard", "Dashboard financeiro"
    SECURITY = "security", "Segurança"
    BACKUP = "backup", "Backups"
    SYSTEM = "system", "Sistema"
    EMAIL = "email", "E-mail"
    FEATUREFLAGS = "featureflags", "Feature flags"
    STATISTICS = "statistics", "Estatísticas"
    PRESCRIPTION = "prescription", "Prescrições"
    TREATMENT = "treatment", "Tratamentos"
    EVOLUTION = "evolution", "Evolução clínica"
    DISCHARGE = "discharge", "Alta médica"
    SEND = "send", "Enviar"
    TEMPLATE = "template", "Templates"
    SETTINGS = "settings", "Configurações"
    HISTORY = "history", "Histórico"


class SystemModule(models.TextChoices):
    PATIENTS = "patients", "Pacientes"
    APPOINTMENTS = "appointments", "Consultas"
    LABORATORY = "laboratory", "Laboratório"
    BILLING = "billing", "Faturação"
    FINANCE = "finance", "Financeiro"
    REPORTS = "reports", "Relatórios"
    DASHBOARD = "dashboard", "Dashboard"
    USERS = "users", "Utilizadores"
    SETTINGS = "settings", "Configurações"
    RECEPTION = "reception", "Receção"
    DOCTORS = "doctors", "Médicos"
    NOTIFICATIONS = "notifications", "Notificações"
    PHARMACY = "pharmacy", "Farmácia de urgência"


class ModulePermission(models.Model):
    module = models.CharField("Módulo", max_length=50, choices=SystemModule.choices)
    action = models.CharField("Ação", max_length=20, choices=PermissionAction.choices)
    codename = models.CharField("Código", max_length=100, unique=True)
    name = models.CharField("Nome", max_length=150)
    description = models.TextField("Descrição", blank=True)

    class Meta:
        verbose_name = "Permissão"
        verbose_name_plural = "Permissões"
        ordering = ["module", "action"]
        unique_together = [("module", "action")]

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        if not self.codename:
            self.codename = f"{self.module}.{self.action}"
        super().save(*args, **kwargs)


class Role(models.Model):
    name = models.CharField("Nome", max_length=100, unique=True)
    slug = models.SlugField("Identificador", max_length=50, unique=True)
    description = models.TextField("Descrição", blank=True)
    is_system = models.BooleanField("Perfil do sistema", default=False)
    permissions = models.ManyToManyField(
        ModulePermission,
        verbose_name="Permissões",
        blank=True,
        related_name="roles",
    )

    class Meta:
        verbose_name = "Perfil"
        verbose_name_plural = "Perfis"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class UserGroup(models.Model):
    name = models.CharField("Nome", max_length=100, unique=True)
    description = models.TextField("Descrição", blank=True)
    permissions = models.ManyToManyField(
        ModulePermission,
        verbose_name="Permissões",
        blank=True,
        related_name="groups",
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        verbose_name="Membros",
        blank=True,
        related_name="custom_groups",
    )
    is_active = models.BooleanField("Ativo", default=True)
    created_at = models.DateTimeField("Criado em", auto_now_add=True)
    updated_at = models.DateTimeField("Atualizado em", auto_now=True)

    class Meta:
        verbose_name = "Grupo"
        verbose_name_plural = "Grupos"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class UserSession(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sessions",
        verbose_name="Utilizador",
    )
    refresh_jti = models.CharField("JTI do refresh token", max_length=255, blank=True)
    ip_address = models.GenericIPAddressField("Endereço IP", null=True, blank=True)
    user_agent = models.TextField("User Agent", blank=True)
    is_active = models.BooleanField("Sessão ativa", default=True)
    created_at = models.DateTimeField("Criado em", auto_now_add=True)
    last_activity = models.DateTimeField("Última atividade", auto_now=True)
    logged_out_at = models.DateTimeField("Terminada em", null=True, blank=True)

    class Meta:
        verbose_name = "Sessão"
        verbose_name_plural = "Sessões"
        ordering = ["-last_activity"]

    def __str__(self) -> str:
        return f"Sessão de {self.user.email}"
