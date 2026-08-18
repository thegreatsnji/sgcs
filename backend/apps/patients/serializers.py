"""Serializers do módulo de pacientes."""

from rest_framework import serializers

from apps.patients.constants import (
    AllergySeverity,
    ChronicDiseaseStatus,
    DocumentType,
    EmergencyRelationship,
    HistoryEventType,
    InsurancePlanType,
    MaritalStatus,
    ObservationType,
    PatientDocumentType,
    PatientGender,
)
from apps.patients.models import (
    Patient,
    PatientAllergy,
    PatientChronicDisease,
    PatientDocument,
    PatientEmergencyContact,
    PatientHistory,
    PatientInsurance,
    PatientObservation,
    PatientPhoto,
)
from apps.patients.services.duplicate_service import DuplicateService
from apps.patients.services.patient_service import PatientService
from apps.patients.validators import (
    validate_birth_date,
    validate_document_expiry,
    validate_insurance_dates,
    validate_patient_phone,
)


class UserSummarySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    full_name = serializers.CharField(source="get_full_name")


class PatientEmergencyContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientEmergencyContact
        fields = (
            "id",
            "name",
            "phone",
            "email",
            "relationship",
            "is_primary",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def validate_phone(self, value):
        return validate_patient_phone(value)

    def validate(self, attrs):
        patient = self.context.get("patient") or getattr(self.instance, "patient", None)
        is_primary = attrs.get(
            "is_primary",
            self.instance.is_primary if self.instance else False,
        )
        if is_primary and patient:
            PatientService.clear_primary_emergency_contacts(
                patient,
                exclude_id=self.instance.pk if self.instance else None,
            )
        return attrs


class PatientInsuranceSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientInsurance
        fields = (
            "id",
            "provider_name",
            "policy_number",
            "plan_type",
            "valid_from",
            "valid_until",
            "is_primary",
            "is_active",
            "notes",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def validate(self, attrs):
        valid_from = attrs.get("valid_from", getattr(self.instance, "valid_from", None))
        valid_until = attrs.get("valid_until", getattr(self.instance, "valid_until", None))
        validate_insurance_dates(valid_from, valid_until)

        patient = self.context.get("patient") or getattr(self.instance, "patient", None)
        is_primary = attrs.get(
            "is_primary",
            self.instance.is_primary if self.instance else False,
        )
        if is_primary and patient:
            PatientService.clear_primary_insurances(
                patient,
                exclude_id=self.instance.pk if self.instance else None,
            )
        return attrs


class PatientAllergySerializer(serializers.ModelSerializer):
    recorded_by = UserSummarySerializer(read_only=True)

    class Meta:
        model = PatientAllergy
        fields = (
            "id",
            "allergen",
            "severity",
            "reaction",
            "diagnosed_at",
            "is_active",
            "notes",
            "recorded_by",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "recorded_by", "created_at", "updated_at")


class PatientChronicDiseaseSerializer(serializers.ModelSerializer):
    recorded_by = UserSummarySerializer(read_only=True)

    class Meta:
        model = PatientChronicDisease
        fields = (
            "id",
            "disease_name",
            "icd_code",
            "diagnosed_at",
            "status",
            "is_active",
            "notes",
            "recorded_by",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "recorded_by", "created_at", "updated_at")


class PatientDocumentSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()
    mime_type = serializers.CharField(source="stored_file.mime_type", read_only=True)
    size = serializers.IntegerField(source="stored_file.size", read_only=True)
    uploaded_by = UserSummarySerializer(read_only=True)
    file = serializers.FileField(write_only=True, required=False)

    class Meta:
        model = PatientDocument
        fields = (
            "id",
            "document_type",
            "title",
            "document_number",
            "description",
            "issued_at",
            "expires_at",
            "is_active",
            "file_url",
            "mime_type",
            "size",
            "uploaded_by",
            "file",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "file_url", "mime_type", "size", "uploaded_by", "created_at", "updated_at")

    def get_file_url(self, obj) -> str | None:
        request = self.context.get("request")
        if obj.stored_file and obj.stored_file.file:
            if request:
                return request.build_absolute_uri(obj.stored_file.file.url)
            return obj.stored_file.file.url
        return None

    def validate(self, attrs):
        issued_at = attrs.get("issued_at", getattr(self.instance, "issued_at", None))
        expires_at = attrs.get("expires_at", getattr(self.instance, "expires_at", None))
        validate_document_expiry(issued_at, expires_at)
        if not self.instance and not attrs.get("file"):
            raise serializers.ValidationError({"file": "O ficheiro é obrigatório."})
        return attrs

    def create(self, validated_data):
        from apps.files.models import StoredFile

        patient = self.context["patient"]
        user = self.context["request"].user
        upload = validated_data.pop("file")
        stored_file = StoredFile.objects.create(
            name=upload.name,
            file=upload,
            mime_type=getattr(upload, "content_type", ""),
            size=upload.size,
            uploaded_by=user,
        )
        return PatientDocument.objects.create(
            patient=patient,
            stored_file=stored_file,
            uploaded_by=user,
            **validated_data,
        )


class PatientPhotoSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()
    uploaded_by = UserSummarySerializer(read_only=True)
    file = serializers.ImageField(write_only=True, required=False)

    class Meta:
        model = PatientPhoto
        fields = (
            "id",
            "is_primary",
            "caption",
            "taken_at",
            "is_active",
            "file_url",
            "uploaded_by",
            "file",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "file_url", "uploaded_by", "created_at", "updated_at")

    def get_file_url(self, obj) -> str | None:
        request = self.context.get("request")
        if obj.stored_file and obj.stored_file.file:
            if request:
                return request.build_absolute_uri(obj.stored_file.file.url)
            return obj.stored_file.file.url
        return None

    def validate(self, attrs):
        if not self.instance and not attrs.get("file"):
            raise serializers.ValidationError({"file": "A imagem é obrigatória."})
        patient = self.context.get("patient") or getattr(self.instance, "patient", None)
        is_primary = attrs.get(
            "is_primary",
            self.instance.is_primary if self.instance else False,
        )
        if is_primary and patient:
            PatientService.clear_primary_photos(
                patient,
                exclude_id=self.instance.pk if self.instance else None,
            )
        return attrs

    def create(self, validated_data):
        from apps.files.models import StoredFile

        patient = self.context["patient"]
        user = self.context["request"].user
        upload = validated_data.pop("file")
        stored_file = StoredFile.objects.create(
            name=upload.name,
            file=upload,
            mime_type=getattr(upload, "content_type", "image/jpeg"),
            size=upload.size,
            uploaded_by=user,
        )
        return PatientPhoto.objects.create(
            patient=patient,
            stored_file=stored_file,
            uploaded_by=user,
            **validated_data,
        )


class PatientHistorySerializer(serializers.ModelSerializer):
    recorded_by = UserSummarySerializer(read_only=True)

    class Meta:
        model = PatientHistory
        fields = (
            "id",
            "event_type",
            "title",
            "description",
            "event_date",
            "source_module",
            "source_id",
            "metadata",
            "recorded_by",
            "created_at",
        )
        read_only_fields = fields


class PatientObservationSerializer(serializers.ModelSerializer):
    created_by = UserSummarySerializer(read_only=True)
    updated_by = UserSummarySerializer(read_only=True)

    class Meta:
        model = PatientObservation
        fields = (
            "id",
            "observation_type",
            "content",
            "is_pinned",
            "is_active",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_by", "updated_by", "created_at", "updated_at")

    def validate_content(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("O conteúdo não pode estar vazio.")
        return value.strip()

    def update(self, instance, validated_data):
        user = self.context["request"].user
        validated_data["updated_by"] = user
        return super().update(instance, validated_data)


class PatientListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = (
            "id",
            "patient_number",
            "full_name",
            "first_name",
            "last_name",
            "document_number",
            "document_type",
            "phone",
            "email",
            "birth_date",
            "gender",
            "is_active",
            "created_at",
        )


class PatientDetailSerializer(serializers.ModelSerializer):
    created_by = UserSummarySerializer(read_only=True)
    updated_by = UserSummarySerializer(read_only=True)
    emergency_contacts = PatientEmergencyContactSerializer(many=True, read_only=True)
    allergies_count = serializers.SerializerMethodField()
    chronic_diseases_count = serializers.SerializerMethodField()
    primary_photo_url = serializers.SerializerMethodField()
    age = serializers.IntegerField(read_only=True, allow_null=True)
    import_origin = serializers.SerializerMethodField()
    verification_state = serializers.SerializerMethodField()
    dados_verificados = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        fields = (
            "id",
            "patient_number",
            "first_name",
            "last_name",
            "full_name",
            "document_type",
            "document_number",
            "birth_date",
            "age",
            "gender",
            "phone",
            "email",
            "address_street",
            "address_city",
            "address_region",
            "address_country",
            "address_postal_code",
            "nationality",
            "blood_type",
            "marital_status",
            "occupation",
            "is_active",
            "is_deleted",
            "deleted_at",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "emergency_contacts",
            "allergies_count",
            "chronic_diseases_count",
            "primary_photo_url",
            "import_origin",
            "verification_state",
            "dados_verificados",
        )
        read_only_fields = (
            "id",
            "patient_number",
            "full_name",
            "is_deleted",
            "deleted_at",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "age",
            "import_origin",
            "verification_state",
            "dados_verificados",
        )

    def get_allergies_count(self, obj) -> int:
        return obj.allergies.filter(is_active=True).count()

    def get_chronic_diseases_count(self, obj) -> int:
        return obj.chronic_diseases.filter(is_active=True).count()

    def get_primary_photo_url(self, obj) -> str | None:
        photo = obj.photos.filter(is_primary=True, is_active=True).select_related("stored_file").first()
        if not photo:
            return None
        request = self.context.get("request")
        if photo.stored_file.file:
            if request:
                return request.build_absolute_uri(photo.stored_file.file.url)
            return photo.stored_file.file.url
        return None

    def get_import_origin(self, obj) -> str:
        meta = obj.metadata if isinstance(obj.metadata, dict) else {}
        return str(meta.get("source") or "")

    def get_verification_state(self, obj) -> str:
        meta = obj.metadata if isinstance(obj.metadata, dict) else {}
        return str(meta.get("verification_state") or "")

    def get_dados_verificados(self, obj) -> bool:
        meta = obj.metadata if isinstance(obj.metadata, dict) else {}
        return bool(meta.get("dados_verificados"))


class PatientCreateSerializer(serializers.ModelSerializer):
    emergency_contacts = PatientEmergencyContactSerializer(many=True, required=False)

    class Meta:
        model = Patient
        fields = (
            "first_name",
            "last_name",
            "document_type",
            "document_number",
            "birth_date",
            "gender",
            "phone",
            "email",
            "address_street",
            "address_city",
            "address_region",
            "address_country",
            "address_postal_code",
            "nationality",
            "blood_type",
            "marital_status",
            "occupation",
            "emergency_contacts",
        )
        extra_kwargs = {
            "document_type": {"required": False, "allow_blank": True},
            "document_number": {"required": False, "allow_blank": True},
            "email": {"required": False, "allow_blank": True},
            "address_street": {"required": False, "allow_blank": True},
            "address_city": {"required": False, "allow_blank": True},
            "address_region": {"required": False, "allow_blank": True},
            "address_country": {"required": False, "allow_blank": True},
            "address_postal_code": {"required": False, "allow_blank": True},
            "nationality": {"required": False, "allow_blank": True},
            "blood_type": {"required": False, "allow_blank": True},
            "marital_status": {"required": False, "allow_blank": True},
            "occupation": {"required": False, "allow_blank": True},
        }

    def validate_phone(self, value):
        return validate_patient_phone(value)

    def validate_birth_date(self, value):
        return validate_birth_date(value)

    def validate_document_number(self, value):
        if value and DuplicateService.document_exists(value):
            raise serializers.ValidationError(
                "Já existe um paciente com este documento de identificação."
            )
        return value

    def create(self, validated_data):
        emergency_contacts = validated_data.pop("emergency_contacts", [])
        user = self.context["request"].user
        request = self.context["request"]
        try:
            return PatientService.create(
                validated_data,
                user=user,
                request=request,
                emergency_contacts=emergency_contacts,
            )
        except ValueError as exc:
            raise serializers.ValidationError(str(exc)) from exc


class PatientUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = (
            "first_name",
            "last_name",
            "document_type",
            "document_number",
            "birth_date",
            "gender",
            "phone",
            "email",
            "address_street",
            "address_city",
            "address_region",
            "address_country",
            "address_postal_code",
            "nationality",
            "blood_type",
            "marital_status",
            "occupation",
        )

    def validate_phone(self, value):
        return validate_patient_phone(value)

    def validate_birth_date(self, value):
        return validate_birth_date(value)

    def validate_document_number(self, value):
        instance = self.instance
        if value and DuplicateService.document_exists(value, exclude_id=instance.pk if instance else None):
            raise serializers.ValidationError(
                "Já existe um paciente com este documento de identificação."
            )
        return value

    def update(self, instance, validated_data):
        user = self.context["request"].user
        request = self.context["request"]
        try:
            return PatientService.update(instance, validated_data, user=user, request=request)
        except ValueError as exc:
            raise serializers.ValidationError(str(exc)) from exc


class DuplicateCheckSerializer(serializers.Serializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    birth_date = serializers.DateField()
    phone = serializers.CharField(required=False, allow_blank=True)
    document_number = serializers.CharField(required=False, allow_blank=True)

    def validate_birth_date(self, value):
        return validate_birth_date(value)


class AuditTrailSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    action = serializers.CharField()
    description = serializers.CharField()
    user = UserSummarySerializer(allow_null=True)
    ip_address = serializers.IPAddressField(allow_null=True)
    metadata = serializers.JSONField()
    created_at = serializers.DateTimeField()
