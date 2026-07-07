"""Serializers do módulo de consultas."""

from rest_framework import serializers

from apps.appointments.models import Appointment
from apps.appointments.services.appointment_service import AppointmentService
from apps.appointments.services.clinical_record_service import ClinicalRecordService
from apps.reception.constants import QueuePriority


class PatientSummarySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    full_name = serializers.CharField()
    patient_number = serializers.CharField()
    phone = serializers.CharField(allow_null=True)


class UserSummarySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    full_name = serializers.CharField(source="get_full_name")


class AppointmentSerializer(serializers.ModelSerializer):
    patient = PatientSummarySerializer(read_only=True)
    doctor = UserSummarySerializer(read_only=True)
    receptionist = UserSummarySerializer(read_only=True)
    created_by = UserSummarySerializer(read_only=True)

    class Meta:
        model = Appointment
        fields = (
            "id",
            "appointment_number",
            "patient",
            "doctor",
            "receptionist",
            "queue_entry",
            "check_in",
            "referral",
            "scheduled_at",
            "consultation_date",
            "started_at",
            "completed_at",
            "duration_minutes",
            "status",
            "priority",
            "chief_complaint",
            "notes",
            "diagnosis",
            "clinical_notes",
            "cancellation_reason",
            "created_by",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class AppointmentCreateSerializer(serializers.Serializer):
    patient_id = serializers.IntegerField()
    doctor_id = serializers.IntegerField(required=False, allow_null=True)
    scheduled_at = serializers.DateTimeField(required=False)
    duration_minutes = serializers.IntegerField(required=False, min_value=5, max_value=480)
    priority = serializers.ChoiceField(choices=QueuePriority.choices, required=False)
    notes = serializers.CharField(required=False, allow_blank=True, default="")
    chief_complaint = serializers.CharField(required=False, allow_blank=True, default="")

    def create(self, validated_data):
        user = self.context["request"].user
        request = self.context["request"]
        try:
            return AppointmentService.criar_consulta(
                patient_id=validated_data["patient_id"],
                user=user,
                scheduled_at=validated_data.get("scheduled_at"),
                doctor_id=validated_data.get("doctor_id"),
                duration_minutes=validated_data.get("duration_minutes") or 30,
                priority=validated_data.get("priority", QueuePriority.NORMAL),
                notes=validated_data.get("notes", ""),
                chief_complaint=validated_data.get("chief_complaint", ""),
                request=request,
            )
        except ValueError as exc:
            raise serializers.ValidationError(str(exc)) from exc


class AppointmentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = (
            "doctor",
            "scheduled_at",
            "duration_minutes",
            "priority",
            "chief_complaint",
            "notes",
        )

    def update(self, instance, validated_data):
        user = self.context["request"].user
        request = self.context["request"]
        if "scheduled_at" in validated_data:
            try:
                return AppointmentService.reagendar_consulta(
                    instance.pk,
                    user,
                    scheduled_at=validated_data["scheduled_at"],
                    doctor_id=validated_data.get("doctor").pk if validated_data.get("doctor") else None,
                    duration_minutes=validated_data.get("duration_minutes"),
                    request=request,
                )
            except ValueError as exc:
                raise serializers.ValidationError(str(exc)) from exc
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class AppointmentRescheduleSerializer(serializers.Serializer):
    scheduled_at = serializers.DateTimeField()
    doctor_id = serializers.IntegerField(required=False, allow_null=True)
    duration_minutes = serializers.IntegerField(required=False, min_value=5, max_value=480)


class AppointmentClinicalUpdateSerializer(serializers.Serializer):
    chief_complaint = serializers.CharField(required=False, allow_blank=True)
    notes = serializers.CharField(required=False, allow_blank=True)
    diagnosis = serializers.CharField(required=False, allow_blank=True)
    clinical_notes = serializers.CharField(required=False, allow_blank=True)

    def update(self, instance, validated_data):
        user = self.context["request"].user
        request = self.context["request"]
        try:
            return ClinicalRecordService.actualizar_campos_legados(
                instance.pk,
                user,
                chief_complaint=validated_data.get("chief_complaint"),
                notes=validated_data.get("notes"),
                diagnosis=validated_data.get("diagnosis"),
                clinical_notes=validated_data.get("clinical_notes"),
                request=request,
            )
        except ValueError as exc:
            raise serializers.ValidationError(str(exc)) from exc


class AppointmentCompleteSerializer(serializers.Serializer):
    diagnosis = serializers.CharField(required=False, allow_blank=True, default="")
    clinical_notes = serializers.CharField(required=False, allow_blank=True, default="")


class AppointmentCancelSerializer(serializers.Serializer):
    reason = serializers.CharField(required=False, allow_blank=True, default="")
