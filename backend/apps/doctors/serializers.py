"""Serializers do módulo Médicos."""

from rest_framework import serializers

from apps.doctors.models import (
    AltaMedica,
    EvolucaoClinica,
    MedicamentoPrescrito,
    PlanoTerapeutico,
    Prescricao,
    SeguimentoClinico,
    Tratamento,
)


class MedicamentoPrescritoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicamentoPrescrito
        fields = "__all__"
        read_only_fields = ("prescricao",)


class PlanoTerapeuticoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanoTerapeutico
        fields = "__all__"


class PrescricaoSerializer(serializers.ModelSerializer):
    medicamentos = MedicamentoPrescritoSerializer(many=True, read_only=True)
    planos = PlanoTerapeuticoSerializer(many=True, read_only=True)
    paciente_nome = serializers.CharField(source="paciente.full_name", read_only=True)

    class Meta:
        model = Prescricao
        fields = "__all__"
        read_only_fields = ("medico", "paciente", "estado")


class PrescricaoCreateSerializer(serializers.Serializer):
    consulta_id = serializers.IntegerField()
    observacoes = serializers.CharField(required=False, allow_blank=True)
    medicamentos = MedicamentoPrescritoSerializer(many=True, required=False)
    plano = serializers.DictField(required=False)


class TratamentoSerializer(serializers.ModelSerializer):
    paciente_nome = serializers.CharField(source="paciente.full_name", read_only=True)

    class Meta:
        model = Tratamento
        fields = "__all__"
        read_only_fields = ("paciente", "responsavel")


class EvolucaoClinicaSerializer(serializers.ModelSerializer):
    class Meta:
        model = EvolucaoClinica
        fields = "__all__"
        read_only_fields = ("paciente", "registado_por")


class AltaMedicaSerializer(serializers.ModelSerializer):
    class Meta:
        model = AltaMedica
        fields = "__all__"
        read_only_fields = ("medico", "paciente")


class SeguimentoClinicoSerializer(serializers.ModelSerializer):
    consulta_agendada_numero = serializers.CharField(
        source="consulta_agendada.appointment_number",
        read_only=True,
    )

    class Meta:
        model = SeguimentoClinico
        fields = "__all__"
        read_only_fields = ("medico", "paciente", "consulta_agendada")
