"""Serializers do módulo de receção."""

from rest_framework import serializers

from apps.reception.constants import QueuePriority, QueueStatus, ReferralDepartment, TriageColor, VisitPurpose
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
    priority = serializers.ChoiceField(choices=QueuePriority.choices, required=False)
    triage_color = serializers.ChoiceField(choices=TriageColor.choices, required=False)
    age_at_check_in = serializers.IntegerField(required=False, min_value=0, max_value=120)
    weight = serializers.DecimalField(max_digits=5, decimal_places=2, required=False, allow_null=True)
    temperature = serializers.DecimalField(max_digits=4, decimal_places=1, required=False, allow_null=True)
    blood_pressure = serializers.CharField(required=False, allow_blank=True, default="", max_length=20)
    height_cm = serializers.IntegerField(required=False, allow_null=True, min_value=30, max_value=250)
    spo2 = serializers.IntegerField(required=False, allow_null=True, min_value=0, max_value=100)
    heart_rate = serializers.IntegerField(required=False, allow_null=True, min_value=20, max_value=250)
    respiratory_rate = serializers.IntegerField(required=False, allow_null=True, min_value=5, max_value=80)
    race = serializers.CharField(required=False, allow_blank=True, default="", max_length=80)
    visit_purpose = serializers.ChoiceField(
        choices=VisitPurpose.choices,
        required=False,
        default=VisitPurpose.CONSULTA,
    )
    symptoms = serializers.CharField(required=False, allow_blank=True, default="")
    notes = serializers.CharField(required=False, allow_blank=True, default="")

    def validate(self, attrs):
        triage_color = attrs.get("triage_color")
        if triage_color:
            if not attrs.get("symptoms"):
                raise serializers.ValidationError({"symptoms": "Descreva os sintomas do paciente."})
            if attrs.get("age_at_check_in") is None:
                raise serializers.ValidationError({"age_at_check_in": "Indique a idade do paciente."})
            if attrs.get("weight") is None:
                raise serializers.ValidationError({"weight": "Indique o peso do paciente."})
            if attrs.get("temperature") is None:
                raise serializers.ValidationError({"temperature": "Indique a temperatura do paciente."})
            if not attrs.get("blood_pressure"):
                raise serializers.ValidationError({"blood_pressure": "Indique a pressão arterial."})
        return attrs

    def create(self, validated_data):
        user = self.context["request"].user
        request = self.context["request"]
        try:
            return ReceptionService.check_in(
                validated_data["patient_id"],
                user,
                priority=validated_data.get("priority", QueuePriority.NORMAL),
                triage_color=validated_data.get("triage_color"),
                age_at_check_in=validated_data.get("age_at_check_in"),
                weight=validated_data.get("weight"),
                temperature=validated_data.get("temperature"),
                blood_pressure=validated_data.get("blood_pressure", ""),
                height_cm=validated_data.get("height_cm"),
                spo2=validated_data.get("spo2"),
                heart_rate=validated_data.get("heart_rate"),
                respiratory_rate=validated_data.get("respiratory_rate"),
                race=validated_data.get("race", ""),
                visit_purpose=validated_data.get("visit_purpose", VisitPurpose.CONSULTA),
                symptoms=validated_data.get("symptoms", ""),
                notes=validated_data.get("notes", ""),
                request=request,
            )
        except ValueError as exc:
            raise serializers.ValidationError(str(exc)) from exc


class WaitingQueueSerializer(serializers.ModelSerializer):
    patient = PatientSummarySerializer(read_only=True)
    priority = serializers.CharField(source="check_in.priority", read_only=True)
    triage_color = serializers.CharField(source="check_in.triage_color", read_only=True)
    symptoms = serializers.CharField(source="check_in.symptoms", read_only=True)
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
            "triage_color",
            "symptoms",
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
    doctor_id = serializers.IntegerField(required=False)
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
                doctor_id=validated_data.get("doctor_id"),
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
            "triage_color",
            "age_at_check_in",
            "age_category_at_check_in",
            "weight",
            "temperature",
            "blood_pressure",
            "height_cm",
            "spo2",
            "heart_rate",
            "respiratory_rate",
            "race",
            "visit_purpose",
            "symptoms",
            "notes",
            "created_at",
        )
