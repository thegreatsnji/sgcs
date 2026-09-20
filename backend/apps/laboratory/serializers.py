"""Serializers do módulo de laboratório."""

from rest_framework import serializers

from apps.laboratory.billing import (
    get_estado_faturacao,
    get_estado_faturacao_label,
    pode_iniciar_processamento,
)
from apps.laboratory.constants import EXAM_CATEGORY_LABELS, RESULTADO_ESTADO_LABELS
from apps.laboratory.models import ExameLaboratorial, PedidoLaboratorial
from apps.laboratory.services.laboratory_service import LaboratoryService
from apps.patients.constants import PatientGender


class PatientSummarySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    full_name = serializers.CharField()
    patient_number = serializers.CharField()
    phone = serializers.CharField(allow_null=True)
    gender = serializers.CharField(allow_null=True, required=False)
    gender_label = serializers.SerializerMethodField()
    birth_date = serializers.DateField(allow_null=True, required=False)
    age_years = serializers.SerializerMethodField()

    def get_gender_label(self, obj) -> str | None:
        gender = getattr(obj, "gender", None)
        if not gender:
            return None
        try:
            return PatientGender(gender).label
        except ValueError:
            return gender

    def get_age_years(self, obj) -> int | None:
        birth = getattr(obj, "birth_date", None)
        if not birth:
            return None
        from django.utils import timezone

        today = timezone.localdate()
        years = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
        return years if years >= 0 else None


class DoctorSummarySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    full_name = serializers.CharField(source="get_full_name")


class ExameLaboratorialSerializer(serializers.ModelSerializer):
    categoria_label = serializers.SerializerMethodField()

    class Meta:
        model = ExameLaboratorial
        fields = (
            "id",
            "nome_exame",
            "categoria",
            "categoria_label",
            "estado",
            "observacoes",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields

    def get_categoria_label(self, obj) -> str:
        return EXAM_CATEGORY_LABELS.get(obj.categoria, obj.categoria)


class PedidoLaboratorialSerializer(serializers.ModelSerializer):
    paciente = PatientSummarySerializer(read_only=True)
    medico = DoctorSummarySerializer(read_only=True)
    exames = ExameLaboratorialSerializer(many=True, read_only=True)
    consulta_id = serializers.IntegerField(source="consulta.id", read_only=True)
    appointment_number = serializers.CharField(source="consulta.appointment_number", read_only=True)
    estado_faturacao = serializers.SerializerMethodField()
    estado_faturacao_label = serializers.SerializerMethodField()
    pode_processar = serializers.SerializerMethodField()
    resultado_estado = serializers.SerializerMethodField()
    resultado_estado_label = serializers.SerializerMethodField()
    estado_operacional_label = serializers.SerializerMethodField()

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
            "estado_faturacao",
            "estado_faturacao_label",
            "pode_processar",
            "resultado_estado",
            "resultado_estado_label",
            "estado_operacional_label",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields

    def get_estado_faturacao(self, obj) -> str:
        return get_estado_faturacao(obj)

    def get_estado_faturacao_label(self, obj) -> str:
        return get_estado_faturacao_label(obj)

    def get_pode_processar(self, obj) -> bool:
        return pode_iniciar_processamento(obj)

    def get_resultado_estado(self, obj) -> str | None:
        resultado = getattr(obj, "resultado", None)
        return resultado.estado if resultado else None

    def get_resultado_estado_label(self, obj) -> str | None:
        estado = self.get_resultado_estado(obj)
        if not estado:
            return None
        return RESULTADO_ESTADO_LABELS.get(estado, estado)

    def get_estado_operacional_label(self, obj) -> str:
        """Copy coerente: se há resultado pendente, não dizer só 'Concluído'."""
        resultado = getattr(obj, "resultado", None)
        if resultado and resultado.estado in {"RESULTADO_PENDENTE", "EM_PROCESSAMENTO"}:
            return "Aguarda validação"
        if resultado and resultado.estado == "VALIDADO":
            return "Validado"
        if resultado and resultado.estado == "ENTREGUE":
            return "Entregue"
        labels = {
            "PENDENTE": "Pendente",
            "RECEBIDO": "Recebido",
            "AGUARDANDO_COLHEITA": "Aguardando colheita",
            "EM_PROCESSAMENTO": "Em processamento",
            "CONCLUIDO": "Processamento concluído",
            "CANCELADO": "Cancelado",
        }
        return labels.get(obj.estado, obj.estado)


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
