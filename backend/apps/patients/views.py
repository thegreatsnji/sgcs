"""Views do módulo de pacientes."""

from django.utils import timezone
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser

from apps.audit_logs.models import AuditAction, AuditLog
from apps.audit_logs.services import AuditService
from apps.patients.filters import PatientFilter, PatientHistoryFilter
from apps.patients.mixins import PatientNestedMixin, SuccessResponseMixin, handle_value_error
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
from apps.patients.permissions import NestedPatientPermissionMixin, PatientPermissionMixin
from apps.patients.serializers import (
    AuditTrailSerializer,
    DuplicateCheckSerializer,
    PatientAllergySerializer,
    PatientChronicDiseaseSerializer,
    PatientCreateSerializer,
    PatientDetailSerializer,
    PatientDocumentSerializer,
    PatientEmergencyContactSerializer,
    PatientHistorySerializer,
    PatientInsuranceSerializer,
    PatientListSerializer,
    PatientObservationSerializer,
    PatientPhotoSerializer,
    PatientUpdateSerializer,
)
from apps.patients.services.duplicate_service import DuplicateService
from apps.patients.services.patient_service import PatientService
from core.pagination import StandardPagination
from core.responses import error_response, success_response


@extend_schema_view(
    list=extend_schema(tags=["Pacientes"]),
    retrieve=extend_schema(tags=["Pacientes"]),
    create=extend_schema(tags=["Pacientes"]),
    update=extend_schema(tags=["Pacientes"]),
    partial_update=extend_schema(tags=["Pacientes"]),
    destroy=extend_schema(tags=["Pacientes"]),
)
class PatientViewSet(PatientPermissionMixin, viewsets.ModelViewSet):
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    pagination_class = StandardPagination
    filterset_class = PatientFilter
    search_fields = [
        "full_name",
        "first_name",
        "last_name",
        "document_number",
        "phone",
        "patient_number",
        "email",
    ]
    ordering_fields = [
        "last_name",
        "first_name",
        "full_name",
        "birth_date",
        "created_at",
        "updated_at",
        "patient_number",
    ]
    ordering = ["last_name", "first_name"]
    http_method_names = ["get", "post", "put", "patch", "delete", "head", "options"]

    def get_queryset(self):
        queryset = Patient.objects.select_related("created_by").order_by("last_name", "first_name")
        if self.action == "retrieve":
            queryset = queryset.prefetch_related(
                "emergency_contacts",
                "insurances",
                "allergies",
                "chronic_diseases",
            )
        if self.action == "list":
            include_deleted = self.request.query_params.get("include_deleted")
            if include_deleted not in ("true", "1") or not self._can_view_deleted():
                queryset = queryset.filter(is_deleted=False)
        elif self.action in ("retrieve", "update", "partial_update", "destroy"):
            if not self._can_view_deleted():
                queryset = queryset.filter(is_deleted=False)
        return queryset

    def _can_view_deleted(self) -> bool:
        user = self.request.user
        if user.is_superuser:
            return True
        from apps.users.services.rbac_service import RBACService

        return RBACService.user_has_permission(user, "patients.admin")

    def get_serializer_class(self):
        if self.action == "create":
            return PatientCreateSerializer
        if self.action in ("update", "partial_update"):
            return PatientUpdateSerializer
        if self.action == "retrieve":
            return PatientDetailSerializer
        if self.action == "check_duplicate":
            return DuplicateCheckSerializer
        return PatientListSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        paginated = self.get_paginated_response(serializer.data)
        return success_response(
            data={
                "count": paginated.data["count"],
                "next": paginated.data["next"],
                "previous": paginated.data["previous"],
                "results": paginated.data["results"],
            },
            message="Listagem obtida com sucesso.",
        )

    def retrieve(self, request, *args, **kwargs):
        serializer = PatientDetailSerializer(self.get_object(), context={"request": request})
        return success_response(data=serializer.data, message="Detalhe obtido com sucesso.")

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        patient = serializer.save()
        data = PatientDetailSerializer(patient, context={"request": request}).data
        return success_response(
            data=data,
            message="Paciente registado com sucesso.",
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        patient = serializer.save()
        data = PatientDetailSerializer(patient, context={"request": request}).data
        return success_response(data=data, message="Paciente atualizado com sucesso.")

    @handle_value_error
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        PatientService.soft_delete(instance, request.user, request)
        return success_response(message="Paciente eliminado com sucesso.", data=None)

    @extend_schema(request=None, responses={200: dict}, tags=["Pacientes"])
    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        instance = self.get_object()
        PatientService.activate(instance, request.user, request)
        data = PatientDetailSerializer(instance, context={"request": request}).data
        return success_response(data=data, message="Paciente ativado com sucesso.")

    @extend_schema(request=None, responses={200: dict}, tags=["Pacientes"])
    @action(detail=True, methods=["post"])
    @handle_value_error
    def deactivate(self, request, pk=None):
        instance = self.get_object()
        PatientService.deactivate(instance, request.user, request)
        return success_response(
            data={"id": instance.pk, "is_active": instance.is_active},
            message="Paciente desativado com sucesso.",
        )

    @extend_schema(request=None, responses={200: dict}, tags=["Pacientes"])
    @action(detail=True, methods=["post"], url_path="confirm-imported-data")
    def confirm_imported_data(self, request, pk=None):
        instance = self.get_object()
        meta = dict(instance.metadata or {})
        if meta.get("source") != "MIGRACAO_EXCEL_SAUVIDA":
            return error_response("Este utente não é um registo histórico importado.", status=status.HTTP_400_BAD_REQUEST)
        provenance = {
            key: meta.get(key)
            for key in ("source", "import_batch", "migration_id", "created_via", "record_class")
        }
        meta["dados_verificados"] = True
        meta["verification_state"] = "VERIFICADO"
        for key, value in provenance.items():
            if value not in (None, ""):
                meta[key] = value
        instance.metadata = meta
        instance.updated_by = request.user
        instance.save(update_fields=["metadata", "updated_by", "updated_at"])
        AuditService.log(
            action=AuditAction.PATIENT_UPDATE,
            user=request.user,
            request=request,
            description="Dados históricos do utente confirmados na receção.",
            resource_type="patient",
            resource_id=str(instance.pk),
            metadata={"verification_state": "VERIFICADO", "source": meta.get("source")},
        )
        data = PatientDetailSerializer(instance, context={"request": request}).data
        return success_response(data=data, message="Dados verificados.")

    @extend_schema(
        parameters=[
            OpenApiParameter("first_name", str, required=True),
            OpenApiParameter("last_name", str, required=True),
            OpenApiParameter("birth_date", str, required=True),
            OpenApiParameter("phone", str, required=False),
            OpenApiParameter("document_number", str, required=False),
        ],
        tags=["Pacientes"],
    )
    @action(detail=False, methods=["get"], url_path="check-duplicate")
    def check_duplicate(self, request):
        serializer = DuplicateCheckSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        matches = DuplicateService.find_potential_duplicates(**serializer.validated_data)
        message = (
            "Foram encontrados possíveis duplicados."
            if matches
            else "Nenhum duplicado encontrado."
        )
        return success_response(
            data={"has_duplicates": bool(matches), "matches": matches},
            message=message,
        )

    @extend_schema(tags=["Pacientes"])
    @action(detail=False, methods=["get"])
    def export(self, request):
        export_format = request.query_params.get("export_format", "csv")
        AuditService.log(
            action=AuditAction.PATIENT_EXPORT,
            user=request.user,
            request=request,
            description=f"Pedido de exportação de pacientes ({export_format}).",
            resource_type="patient",
            metadata={"format": export_format},
        )
        return success_response(
            data={"formats": ["csv", "xlsx"], "ready": False},
            message="Exportação em desenvolvimento.",
        )

    @extend_schema(tags=["Pacientes"])
    @action(detail=True, methods=["get"])
    def print(self, request, pk=None):
        instance = self.get_object()
        AuditService.log(
            action=AuditAction.PATIENT_PRINT,
            user=request.user,
            request=request,
            description=f"Pedido de impressão da ficha do paciente {instance.patient_number}.",
            resource_type="patient",
            resource_id=str(instance.pk),
            metadata={"patient_number": instance.patient_number},
        )
        return success_response(
            data={"ready": False, "patient_id": int(pk)},
            message="Impressão de ficha em desenvolvimento.",
        )

    @extend_schema(tags=["Pacientes"])
    @action(detail=True, methods=["get"], url_path="audit-trail")
    def audit_trail(self, request, pk=None):
        queryset = AuditLog.objects.filter(
            resource_type="patient",
            resource_id=str(pk),
        ).select_related("user").order_by("-created_at")
        page = self.paginate_queryset(queryset)
        results = []
        for log in page:
            results.append(
                {
                    "id": log.pk,
                    "action": log.action,
                    "description": log.description,
                    "user": (
                        {"id": log.user_id, "full_name": log.user.get_full_name()}
                        if log.user
                        else None
                    ),
                    "ip_address": log.ip_address,
                    "metadata": log.metadata,
                    "created_at": log.created_at,
                }
            )
        paginated = self.get_paginated_response(results)
        return success_response(
            data={
                "count": paginated.data["count"],
                "next": paginated.data["next"],
                "previous": paginated.data["previous"],
                "results": paginated.data["results"],
            },
            message="Histórico de auditoria obtido com sucesso.",
        )

    @extend_schema(tags=["Pacientes — Integrações"])
    @action(detail=True, methods=["get"])
    def appointments(self, request, pk=None):
        from apps.appointments.serializers import AppointmentSerializer
        from apps.appointments.services.appointment_service import AppointmentService

        patient = self.get_object()
        queryset = AppointmentService.list_for_patient(patient.pk)
        page = self.paginate_queryset(queryset)
        serializer = AppointmentSerializer(page, many=True)
        paginated = self.get_paginated_response(serializer.data)
        return success_response(
            data={
                "count": paginated.data["count"],
                "next": paginated.data["next"],
                "previous": paginated.data["previous"],
                "results": paginated.data["results"],
                "module_ready": True,
            },
            message="Consultas do paciente obtidas com sucesso.",
        )

    @extend_schema(tags=["Pacientes — Integrações"])
    @action(detail=True, methods=["get"], url_path="lab-orders")
    def lab_orders(self, request, pk=None):
        return success_response(
            data={"count": 0, "next": None, "previous": None, "results": [], "module_ready": False},
            message="Módulo de laboratório em desenvolvimento.",
        )

    @extend_schema(tags=["Pacientes — Integrações"])
    @action(detail=True, methods=["get"])
    def prescriptions(self, request, pk=None):
        return success_response(
            data={"count": 0, "next": None, "previous": None, "results": [], "module_ready": False},
            message="Módulo de receitas em desenvolvimento.",
        )

    @extend_schema(tags=["Pacientes — Integrações"])
    @action(detail=True, methods=["get"])
    def payments(self, request, pk=None):
        return success_response(
            data={"count": 0, "next": None, "previous": None, "results": [], "module_ready": False},
            message="Módulo de pagamentos em desenvolvimento.",
        )

    @extend_schema(tags=["Pacientes — Integrações"])
    @action(detail=True, methods=["get"])
    def balance(self, request, pk=None):
        return success_response(
            data={
                "patient_id": int(pk),
                "total_invoiced": "0.00",
                "total_paid": "0.00",
                "balance": "0.00",
                "currency": "XOF",
                "module_ready": False,
            },
            message="Saldo em desenvolvimento.",
        )


class BaseNestedPatientViewSet(
    NestedPatientPermissionMixin,
    PatientNestedMixin,
    SuccessResponseMixin,
    viewsets.ModelViewSet,
):
    pagination_class = StandardPagination
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    list_message = "Listagem obtida com sucesso."
    create_message = "Registo criado com sucesso."
    update_message = "Registo atualizado com sucesso."
    delete_message = "Registo eliminado com sucesso."

    def get_serializer_context(self):
        context = super().get_serializer_context()
        if "patient_pk" in self.kwargs:
            context["patient"] = self.get_patient()
        return context

    def perform_create(self, serializer):
        patient = self.get_patient()
        user = self.request.user
        extra = {"patient": patient}
        model = serializer.Meta.model
        if hasattr(model, "created_by"):
            extra["created_by"] = user
        if hasattr(model, "recorded_by"):
            extra["recorded_by"] = user
        if hasattr(model, "uploaded_by"):
            extra["uploaded_by"] = user
        if hasattr(model, "updated_by"):
            extra["updated_by"] = user
        serializer.save(**extra)

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save(update_fields=["is_active", "updated_at"])


@extend_schema_view(list=extend_schema(tags=["Pacientes — Emergência"]))
class PatientEmergencyContactViewSet(BaseNestedPatientViewSet):
    queryset = PatientEmergencyContact.objects.filter(is_active=True)
    serializer_class = PatientEmergencyContactSerializer
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]


@extend_schema_view(list=extend_schema(tags=["Pacientes — Seguros"]))
class PatientInsuranceViewSet(BaseNestedPatientViewSet):
    queryset = PatientInsurance.objects.filter(is_active=True)
    serializer_class = PatientInsuranceSerializer
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]


@extend_schema_view(list=extend_schema(tags=["Pacientes — Clínica"]))
class PatientAllergyViewSet(BaseNestedPatientViewSet):
    queryset = PatientAllergy.objects.filter(is_active=True)
    serializer_class = PatientAllergySerializer
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]


@extend_schema_view(list=extend_schema(tags=["Pacientes — Clínica"]))
class PatientChronicDiseaseViewSet(BaseNestedPatientViewSet):
    queryset = PatientChronicDisease.objects.filter(is_active=True)
    serializer_class = PatientChronicDiseaseSerializer
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]


@extend_schema_view(list=extend_schema(tags=["Pacientes — Documentos"]))
class PatientDocumentViewSet(BaseNestedPatientViewSet):
    queryset = PatientDocument.objects.filter(is_active=True).select_related("stored_file")
    serializer_class = PatientDocumentSerializer
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]


@extend_schema_view(list=extend_schema(tags=["Pacientes — Documentos"]))
class PatientPhotoViewSet(BaseNestedPatientViewSet):
    queryset = PatientPhoto.objects.filter(is_active=True).select_related("stored_file")
    serializer_class = PatientPhotoSerializer
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    @extend_schema(request=None, tags=["Pacientes — Documentos"])
    @action(detail=True, methods=["post"], url_path="set-primary")
    def set_primary(self, request, patient_pk=None, pk=None):
        photo = self.get_object()
        PatientService.clear_primary_photos(photo.patient, exclude_id=photo.pk)
        photo.is_primary = True
        photo.save(update_fields=["is_primary", "updated_at"])
        serializer = self.get_serializer(photo)
        return success_response(data=serializer.data, message="Fotografia principal definida.")


@extend_schema_view(list=extend_schema(tags=["Pacientes — Histórico"]))
class PatientHistoryViewSet(
    NestedPatientPermissionMixin,
    PatientNestedMixin,
    SuccessResponseMixin,
    viewsets.ReadOnlyModelViewSet,
):
    queryset = PatientHistory.objects.all()
    serializer_class = PatientHistorySerializer
    pagination_class = StandardPagination
    filterset_class = PatientHistoryFilter
    ordering_fields = ["event_date", "created_at"]
    ordering = ["-event_date"]
    http_method_names = ["get", "head", "options"]


@extend_schema_view(list=extend_schema(tags=["Pacientes — Clínica"]))
class PatientObservationViewSet(BaseNestedPatientViewSet):
    queryset = PatientObservation.objects.filter(is_active=True)
    serializer_class = PatientObservationSerializer
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    @extend_schema(request=None, tags=["Pacientes — Clínica"])
    @action(detail=True, methods=["post"])
    def pin(self, request, patient_pk=None, pk=None):
        observation = self.get_object()
        observation.is_pinned = True
        observation.updated_by = request.user
        observation.save(update_fields=["is_pinned", "updated_by", "updated_at"])
        return success_response(
            data=self.get_serializer(observation).data,
            message="Observação fixada.",
        )

    @extend_schema(request=None, tags=["Pacientes — Clínica"])
    @action(detail=True, methods=["post"])
    def unpin(self, request, patient_pk=None, pk=None):
        observation = self.get_object()
        observation.is_pinned = False
        observation.updated_by = request.user
        observation.save(update_fields=["is_pinned", "updated_by", "updated_at"])
        return success_response(
            data=self.get_serializer(observation).data,
            message="Observação desafixada.",
        )
