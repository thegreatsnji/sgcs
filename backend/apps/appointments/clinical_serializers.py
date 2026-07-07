"""Serializers do Prontuário Clínico Eletrónico (PCE)."""

from rest_framework import serializers

from apps.appointments.constants import DiagnosticoTipo
from apps.reception.constants import QueuePriority


class SinaisVitaisSerializer(serializers.Serializer):
    pressao_arterial = serializers.CharField(required=False, allow_blank=True, default="")
    frequencia_cardiaca = serializers.IntegerField(required=False, allow_null=True, min_value=0)
    frequencia_respiratoria = serializers.IntegerField(required=False, allow_null=True, min_value=0)
    temperatura = serializers.DecimalField(
        required=False,
        allow_null=True,
        max_digits=4,
        decimal_places=1,
    )
    saturacao_oxigenio = serializers.IntegerField(required=False, allow_null=True, min_value=0, max_value=100)
    peso = serializers.DecimalField(required=False, allow_null=True, max_digits=6, decimal_places=2)
    altura = serializers.DecimalField(required=False, allow_null=True, max_digits=5, decimal_places=1)
    observacoes = serializers.CharField(required=False, allow_blank=True, default="")


class SOAPSerializer(serializers.Serializer):
    subjetivo = serializers.CharField(required=False, allow_blank=True, default="")
    objetivo = serializers.CharField(required=False, allow_blank=True, default="")
    avaliacao = serializers.CharField(required=False, allow_blank=True, default="")
    plano = serializers.CharField(required=False, allow_blank=True, default="")


class DiagnosticoCreateSerializer(serializers.Serializer):
    codigo_cid10 = serializers.CharField(max_length=20)
    descricao = serializers.CharField(max_length=255)
    tipo = serializers.ChoiceField(choices=DiagnosticoTipo.choices, default=DiagnosticoTipo.PRINCIPAL)


class PedidoExameSerializer(serializers.Serializer):
    tipo_exame = serializers.CharField(max_length=150)
    prioridade = serializers.ChoiceField(choices=QueuePriority.choices, default=QueuePriority.NORMAL)
    observacoes = serializers.CharField(required=False, allow_blank=True, default="")


class SeguimentoSerializer(serializers.Serializer):
    data_retorno = serializers.DateField()
    motivo = serializers.CharField(max_length=255)
    observacoes = serializers.CharField(required=False, allow_blank=True, default="")


class ClinicalRecordPatchSerializer(serializers.Serializer):
    """Campos legados da consulta + SOAP opcional num único PATCH."""

    chief_complaint = serializers.CharField(required=False, allow_blank=True)
    notes = serializers.CharField(required=False, allow_blank=True)
    diagnosis = serializers.CharField(required=False, allow_blank=True)
    clinical_notes = serializers.CharField(required=False, allow_blank=True)
    subjetivo = serializers.CharField(required=False, allow_blank=True)
    objetivo = serializers.CharField(required=False, allow_blank=True)
    avaliacao = serializers.CharField(required=False, allow_blank=True)
    plano = serializers.CharField(required=False, allow_blank=True)
