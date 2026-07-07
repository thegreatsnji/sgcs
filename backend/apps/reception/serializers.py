"""Serializers do módulo de receção."""

from rest_framework import serializers

from apps.reception.constants import QueuePriority, QueueStatus, ReferralDepartment
from apps.reception.models import ReceptionCheckIn, Referral, WaitingQueue
from apps.reception.services.reception_service import ReceptionService


class PatientSummarySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    full_name = serializers.CharField()
    patient_number = serializers.CharField()
    phone = serializers.CharField(allow_null=True)


class UserSummarySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    full_name = serializers.CharField(source="get_full_name")


class CheckInCreateSerializer(serializers.Serializer):
    patient_id = serializers.IntegerField()
    priority = serializers.ChoiceField(choices=QueuePriority.choices, default=QueuePriority.NORMAL)
    notes = serializers.CharField(required=False, allow_blank=True, default="")

    def create(self, validated_data):
        user = self.context["request"].user
        request = self.context["request"]
        try:
            return ReceptionService.check_in(
                validated_data["patient_id"],
                user,
                priority=validated_data.get("priority", QueuePriority.NORMAL),
                notes=validated_data.get("notes", ""),
                request=request,
            )
        except ValueError as exc:
            raise serializers.ValidationError(str(exc)) from exc


class WaitingQueueSerializer(serializers.ModelSerializer):
    patient = PatientSummarySerializer(read_only=True)
    priority = serializers.CharField(source="check_in.priority", read_only=True)
    check_in_time = serializers.DateTimeField(source="check_in.check_in_time", read_only=True)
    receptionist = UserSummarySerializer(source="check_in.receptionist", read_only=True)
    check_in_id = serializers.IntegerField(source="check_in.id", read_only=True)

    class Meta:
        model = WaitingQueue
        fields = (
            "id",
            "check_in_id",
            "patient",
            "position",
            "estimated_wait_minutes",
            "status",
            "priority",
            "check_in_time",
            "receptionist",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class WaitingQueueUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = WaitingQueue
        fields = ("status",)

    def validate_status(self, value):
        if value not in dict(QueueStatus.choices):
            raise serializers.ValidationError("Estado inválido.")
        return value

    def update(self, instance, validated_data):
        user = self.context["request"].user
        request = self.context["request"]
        status = validated_data.get("status")
        try:
            return ReceptionService.update_queue_entry(
                instance.pk,
                user,
                status=status,
                request=request,
            )
        except ValueError as exc:
            raise serializers.ValidationError(str(exc)) from exc


class AssignToDoctorSerializer(serializers.Serializer):
    queue_id = serializers.IntegerField(required=False)
    check_in_id = serializers.IntegerField(required=False)
    reason = serializers.CharField(required=False, allow_blank=True, default="")

    def validate(self, attrs):
        if not attrs.get("queue_id") and not attrs.get("check_in_id"):
            raise serializers.ValidationError("Indique queue_id ou check_in_id.")
        return attrs

    def create(self, validated_data):
        user = self.context["request"].user
        request = self.context["request"]
        try:
            return ReceptionService.assign_to_doctor(
                queue_id=validated_data.get("queue_id"),
                check_in_id=validated_data.get("check_in_id"),
                user=user,
                reason=validated_data.get("reason", ""),
                request=request,
            )
        except ValueError as exc:
            raise serializers.ValidationError(str(exc)) from exc


class ReferralCreateSerializer(serializers.Serializer):
    patient_id = serializers.IntegerField()
    check_in_id = serializers.IntegerField(required=False, allow_null=True)
    to_department = serializers.ChoiceField(choices=ReferralDepartment.choices)
    reason = serializers.CharField()

    def create(self, validated_data):
        from apps.patients.services.patient_service import PatientService

        user = self.context["request"].user
        request = self.context["request"]
        patient = PatientService.get_active_queryset().get(pk=validated_data["patient_id"])
        check_in = None
        if validated_data.get("check_in_id"):
            check_in = ReceptionCheckIn.objects.filter(pk=validated_data["check_in_id"]).first()

        referral = Referral.objects.create(
            patient=patient,
            check_in=check_in,
            from_department=ReferralDepartment.RECEPTION,
            to_department=validated_data["to_department"],
            reason=validated_data["reason"],
            referred_by=user,
        )

        from apps.audit_logs.models import AuditAction
        from apps.audit_logs.services import AuditService

        AuditService.log(
            action=AuditAction.RECEPTION_REFERRAL,
            user=user,
            request=request,
            description=f"Encaminhamento de {patient.full_name} para {validated_data['to_department']}.",
            resource_type="referral",
            resource_id=str(referral.pk),
            metadata={"patient_id": patient.pk, "to_department": validated_data["to_department"]},
        )
        return referral


class ReferralSerializer(serializers.ModelSerializer):
    patient = PatientSummarySerializer(read_only=True)
    referred_by = UserSummarySerializer(read_only=True)

    class Meta:
        model = Referral
        fields = (
            "id",
            "patient",
            "check_in",
            "from_department",
            "to_department",
            "reason",
            "referred_by",
            "created_at",
        )


class ReceptionCheckInSerializer(serializers.ModelSerializer):
    patient = PatientSummarySerializer(read_only=True)
    receptionist = UserSummarySerializer(read_only=True)

    class Meta:
        model = ReceptionCheckIn
        fields = (
            "id",
            "patient",
            "receptionist",
            "check_in_time",
            "status",
            "priority",
            "notes",
            "created_at",
        )
