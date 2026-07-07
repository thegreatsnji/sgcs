"""Serializers do módulo Notificações."""

from rest_framework import serializers

from apps.notifications.models import (
    HistoricoEmail,
    HistoricoSMS,
    Notificacao,
    PreferenciaNotificacao,
    TemplateEmail,
    TemplateSMS,
)


class NotificacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notificacao
        fields = [
            "id",
            "titulo",
            "mensagem",
            "tipo",
            "canal",
            "estado",
            "evento_origem",
            "metadados",
            "lida",
            "lida_em",
            "arquivada",
            "destinatario_email",
            "destinatario_telefone",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "estado", "lida_em", "created_at", "updated_at"]


class NotificacaoCreateSerializer(serializers.Serializer):
    titulo = serializers.CharField(max_length=255)
    mensagem = serializers.CharField()
    utilizador_id = serializers.IntegerField(required=False)
    tipo = serializers.CharField(required=False, default="INFORMATIVA")
    canal = serializers.CharField(required=False, default="INTERNO")
    destinatario_email = serializers.EmailField(required=False, allow_blank=True)
    destinatario_telefone = serializers.CharField(required=False, allow_blank=True)


class TemplateEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = TemplateEmail
        fields = ["id", "codigo", "nome", "assunto", "corpo", "activo", "variaveis", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class TemplateSMSSerializer(serializers.ModelSerializer):
    class Meta:
        model = TemplateSMS
        fields = ["id", "codigo", "nome", "mensagem", "activo", "variaveis", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class TemplatePreviewSerializer(serializers.Serializer):
    contexto = serializers.DictField(child=serializers.CharField(), required=False, default=dict)


class PreferenciaNotificacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PreferenciaNotificacao
        fields = [
            "id",
            "receber_email",
            "receber_sms",
            "receber_internas",
            "receber_lembretes",
            "receber_alertas_admin",
            "updated_at",
        ]
        read_only_fields = ["id", "updated_at"]


class HistoricoEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoricoEmail
        fields = ["id", "destinatario", "assunto", "estado", "erro", "enviado_em"]


class HistoricoSMSSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoricoSMS
        fields = ["id", "telefone", "estado", "erro", "enviado_em"]


class EmailTestSerializer(serializers.Serializer):
    destinatario = serializers.EmailField()


class SMSTestSerializer(serializers.Serializer):
    telefone = serializers.CharField(max_length=30)
