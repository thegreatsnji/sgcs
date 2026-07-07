"""Modelos do módulo Notificações."""

from django.conf import settings
from django.db import models

from apps.notifications.constants import NotificacaoCanal, NotificacaoEstado, NotificacaoTipo
from core.mixins import TimestampMixin


class Notificacao(TimestampMixin):
    utilizador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notificacoes",
        verbose_name="Utilizador",
        null=True,
        blank=True,
    )
    titulo = models.CharField("Título", max_length=255)
    mensagem = models.TextField("Mensagem")
    tipo = models.CharField(
        "Tipo",
        max_length=20,
        choices=NotificacaoTipo.CHOICES,
        default=NotificacaoTipo.INFORMATIVA,
    )
    canal = models.CharField(
        "Canal",
        max_length=20,
        choices=NotificacaoCanal.CHOICES,
        default=NotificacaoCanal.INTERNO,
    )
    estado = models.CharField(
        "Estado",
        max_length=20,
        choices=NotificacaoEstado.CHOICES,
        default=NotificacaoEstado.PENDENTE,
    )
    evento_origem = models.CharField("Evento de origem", max_length=100, blank=True)
    metadados = models.JSONField("Metadados", default=dict, blank=True)
    lida = models.BooleanField("Lida", default=False)
    lida_em = models.DateTimeField("Lida em", null=True, blank=True)
    arquivada = models.BooleanField("Arquivada", default=False)
    destinatario_email = models.EmailField("E-mail destinatário", blank=True)
    destinatario_telefone = models.CharField("Telefone destinatário", max_length=30, blank=True)

    class Meta:
        verbose_name = "Notificação"
        verbose_name_plural = "Notificações"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["utilizador", "lida", "arquivada"]),
            models.Index(fields=["estado"]),
            models.Index(fields=["canal"]),
        ]

    def __str__(self) -> str:
        return f"{self.titulo} ({self.estado})"


class TemplateEmail(TimestampMixin):
    codigo = models.SlugField("Código", max_length=80, unique=True)
    nome = models.CharField("Nome", max_length=150)
    assunto = models.CharField("Assunto", max_length=255)
    corpo = models.TextField("Corpo")
    activo = models.BooleanField("Activo", default=True)
    variaveis = models.JSONField("Variáveis disponíveis", default=list, blank=True)

    class Meta:
        verbose_name = "Template de e-mail"
        verbose_name_plural = "Templates de e-mail"
        ordering = ["nome"]

    def __str__(self) -> str:
        return self.nome


class TemplateSMS(TimestampMixin):
    codigo = models.SlugField("Código", max_length=80, unique=True)
    nome = models.CharField("Nome", max_length=150)
    mensagem = models.TextField("Mensagem")
    activo = models.BooleanField("Activo", default=True)
    variaveis = models.JSONField("Variáveis disponíveis", default=list, blank=True)

    class Meta:
        verbose_name = "Template SMS"
        verbose_name_plural = "Templates SMS"
        ordering = ["nome"]

    def __str__(self) -> str:
        return self.nome


class PreferenciaNotificacao(TimestampMixin):
    utilizador = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="preferencias_notificacao",
        verbose_name="Utilizador",
    )
    receber_email = models.BooleanField("Receber e-mail", default=True)
    receber_sms = models.BooleanField("Receber SMS", default=False)
    receber_internas = models.BooleanField("Receber notificações internas", default=True)
    receber_lembretes = models.BooleanField("Receber lembretes", default=True)
    receber_alertas_admin = models.BooleanField("Receber alertas administrativos", default=True)

    class Meta:
        verbose_name = "Preferência de notificação"
        verbose_name_plural = "Preferências de notificação"

    def __str__(self) -> str:
        return f"Preferências — {self.utilizador}"


class HistoricoEmail(TimestampMixin):
    destinatario = models.EmailField("Destinatário")
    assunto = models.CharField("Assunto", max_length=255)
    corpo = models.TextField("Corpo")
    estado = models.CharField(
        "Estado",
        max_length=20,
        choices=NotificacaoEstado.CHOICES,
        default=NotificacaoEstado.ENVIADA,
    )
    erro = models.TextField("Erro", blank=True)
    notificacao = models.ForeignKey(
        Notificacao,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="emails",
        verbose_name="Notificação",
    )
    enviado_em = models.DateTimeField("Enviado em", auto_now_add=True)

    class Meta:
        verbose_name = "Histórico de e-mail"
        verbose_name_plural = "Histórico de e-mails"
        ordering = ["-enviado_em"]


class HistoricoSMS(TimestampMixin):
    telefone = models.CharField("Telefone", max_length=30)
    mensagem = models.TextField("Mensagem")
    estado = models.CharField(
        "Estado",
        max_length=20,
        choices=NotificacaoEstado.CHOICES,
        default=NotificacaoEstado.ENVIADA,
    )
    erro = models.TextField("Erro", blank=True)
    notificacao = models.ForeignKey(
        Notificacao,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sms",
        verbose_name="Notificação",
    )
    enviado_em = models.DateTimeField("Enviado em", auto_now_add=True)

    class Meta:
        verbose_name = "Histórico SMS"
        verbose_name_plural = "Histórico SMS"
        ordering = ["-enviado_em"]


class FilaNotificacao(TimestampMixin):
    notificacao = models.ForeignKey(
        Notificacao,
        on_delete=models.CASCADE,
        related_name="fila",
        verbose_name="Notificação",
    )
    prioridade = models.PositiveSmallIntegerField("Prioridade", default=5)
    tentativas = models.PositiveSmallIntegerField("Tentativas", default=0)
    max_tentativas = models.PositiveSmallIntegerField("Máximo de tentativas", default=3)
    agendado_para = models.DateTimeField("Agendado para", null=True, blank=True)
    processado_em = models.DateTimeField("Processado em", null=True, blank=True)
    erro = models.TextField("Erro", blank=True)

    class Meta:
        verbose_name = "Fila de notificação"
        verbose_name_plural = "Fila de notificações"
        ordering = ["prioridade", "created_at"]
