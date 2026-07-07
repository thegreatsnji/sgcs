"""Serializers do módulo de laboratório."""

from rest_framework import serializers

from apps.laboratory.models import ExameLaboratorial, PedidoLaboratorial
from apps.laboratory.services.laboratory_service import LaboratoryService


class PatientSummarySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    full_name = serializers.CharField()
    patient_number = serializers.CharField()
    phone = serializers.CharField(allow_null=True)


class DoctorSummarySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    full_name = serializers.CharField(source="get_full_name")


class ExameLaboratorialSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExameLaboratorial
        fields = ("id", "nome_exame", "categoria", "estado", "observacoes", "created_at", "updated_at")
        read_only_fields = fields


class PedidoLaboratorialSerializer(serializers.ModelSerializer):
    paciente = PatientSummarySerializer(read_only=True)
    medico = DoctorSummarySerializer(read_only=True)
    exames = ExameLaboratorialSerializer(many=True, read_only=True)
    consulta_id = serializers.IntegerField(source="consulta.id", read_only=True)
    appointment_number = serializers.CharField(source="consulta.appointment_number", read_only=True)

    class Meta:
        model = PedidoLaboratorial
        fields = (
            "id",
            "numero_pedido",
            "consulta_id",
            "appointment_number",
            "paciente",
            "medico",
            "estado",
            "prioridade",
            "data_pedido",
            "data_rececao",
            "data_colheita",
            "data_conclusao",
            "observacoes",
            "exames",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class PedidoLaboratorialUpdateSerializer(serializers.Serializer):
    observacoes = serializers.CharField(required=False, allow_blank=True)
    prioridade = serializers.CharField(required=False)

    def update(self, instance, validated_data):
        user = self.context["request"].user
        request = self.context["request"]
        try:
            return LaboratoryService.actualizar_pedido(
                instance.pk,
                user,
                observacoes=validated_data.get("observacoes"),
                prioridade=validated_data.get("prioridade"),
                request=request,
            )
        except ValueError as exc:
            raise serializers.ValidationError(str(exc)) from exc
