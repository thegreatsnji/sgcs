"""Views do módulo de consultas."""

from datetime import datetime

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action

from apps.appointments.filters import AppointmentFilter
from apps.appointments.models import Appointment
from apps.appointments.permissions import AppointmentPermissionMixin
from apps.appointments.serializers import (
    AppointmentCancelSerializer,
    AppointmentClinicalUpdateSerializer,
    AppointmentCompleteSerializer,
    AppointmentCreateSerializer,
    AppointmentRescheduleSerializer,
    AppointmentSerializer,
    AppointmentUpdateSerializer,
)
from apps.appointments.clinical_serializers import (
    ClinicalRecordPatchSerializer,
    DiagnosticoCreateSerializer,
    PedidoExameSerializer,
    SeguimentoSerializer,
    SinaisVitaisSerializer,
    SOAPSerializer,
)
from apps.appointments.services.appointment_service import AppointmentService
from apps.appointments.services.clinical_record_service import ClinicalRecordService
from core.pagination import StandardPagination
from core.responses import error_response, success_response


@extend_schema_view(
    list=extend_schema(tags=["Consultas"]),
    retrieve=extend_schema(tags=["Consultas"]),
    create=extend_schema(tags=["Consultas"]),
    partial_update=extend_schema(tags=["Consultas"]),
    destroy=extend_schema(tags=["Consultas"]),
    queue=extend_schema(tags=["Consultas"]),
    today=extend_schema(tags=["Consultas"]),
    doctor=extend_schema(tags=["Consultas"]),
    calendar=extend_schema(tags=["Consultas"]),
    confirm=extend_schema(tags=["Consultas"]),
    start=extend_schema(tags=["Consultas"]),
    complete=extend_schema(tags=["Consultas"]),
    finish=extend_schema(tags=["Consultas"]),
    cancel=extend_schema(tags=["Consultas"]),
    clinical_record=extend_schema(tags=["Prontuário Clínico"]),
    vital_signs=extend_schema(tags=["Prontuário Clínico"]),
    diagnoses=extend_schema(tags=["Prontuário Clínico"]),
    laboratory=extend_schema(tags=["Prontuário Clínico"]),
    imaging=extend_schema(tags=["Prontuário Clínico"]),
    follow_up=extend_schema(tags=["Prontuário Clínico"]),
)
class AppointmentViewSet(AppointmentPermissionMixin, viewsets.ModelViewSet):
    queryset = (
        Appointment.objects.select_related("patient", "doctor", "receptionist", "created_by")
        .order_by("-scheduled_at")
    )
    serializer_class = AppointmentSerializer
    pagination_class = StandardPagination
    filterset_class = AppointmentFilter
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    @property
    def required_permission(self) -> str:
        if self.action == "clinical_record" and self.request.method == "GET":
            return "appointments.view"
        return self.permission_map.get(self.action, self.default_permission)

    def get_serializer_class(self):
        if self.action == "create":
            return AppointmentCreateSerializer
        if self.action in {"partial_update", "update"}:
            return AppointmentUpdateSerializer
        return AppointmentSerializer

    def _paginated_response(self, queryset, message: str):
        page = self.paginate_queryset(queryset)
        serializer = AppointmentSerializer(page, many=True)
        paginated = self.get_paginated_response(serializer.data)
        return success_response(
            data={
                "count": paginated.data["count"],
                "next": paginated.data["next"],
                "previous": paginated.data["previous"],
                "results": paginated.data["results"],
            },
            message=message,
        )

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        return self._paginated_response(queryset, "Consultas obtidas com sucesso.")

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        return success_response(
            data=AppointmentSerializer(instance).data,
            message="Consulta obtida com sucesso.",
        )

    def create(self, request, *args, **kwargs):
        serializer = AppointmentCreateSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        appointment = serializer.save()
        return success_response(
            data=AppointmentSerializer(appointment).data,
            message="Consulta criada com sucesso.",
            status=status.HTTP_201_CREATED,
        )

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = AppointmentUpdateSerializer(
            instance,
            data=request.data,
            partial=True,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        updated = serializer.save()
        return success_response(
            data=AppointmentSerializer(updated).data,
            message="Consulta actualizada com sucesso.",
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.status not in {"AGENDADA", "CONFIRMADA"}:
            return error_response(
                "Apenas consultas agendadas podem ser eliminadas.",
                status=status.HTTP_400_BAD_REQUEST,
            )
        instance.delete()
        return success_response(message="Consulta eliminada com sucesso.", status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="queue")
    def queue(self, request):
        queryset = AppointmentService.get_doctor_queue(request.user)
        return self._paginated_response(queryset, "Fila de consultas obtida com sucesso.")

    @action(detail=False, methods=["get"], url_path="today")
    def today(self, request):
        doctor_id = request.query_params.get("doctor")
        queryset = AppointmentService.listar_consultas_do_dia(
            doctor_id=int(doctor_id) if doctor_id else None,
        )
        return self._paginated_response(queryset, "Consultas do dia obtidas com sucesso.")

    @action(detail=False, methods=["get"], url_path="doctor")
    def doctor(self, request):
        doctor_id = request.query_params.get("doctor_id") or request.user.pk
        day = request.query_params.get("date")
        parsed_day = datetime.strptime(day, "%Y-%m-%d").date() if day else None
        queryset = AppointmentService.listar_consultas_do_medico(int(doctor_id), day=parsed_day)
        return self._paginated_response(queryset, "Consultas do médico obtidas com sucesso.")

    @action(detail=False, methods=["get"], url_path="calendar")
    def calendar(self, request):
        start = request.query_params.get("start")
        end = request.query_params.get("end")
        if not start or not end:
            return error_response("Indique os parâmetros start e end (YYYY-MM-DD).", status=400)
        doctor_id = request.query_params.get("doctor_id")
        queryset = AppointmentService.get_calendar(
            start_date=datetime.strptime(start, "%Y-%m-%d").date(),
            end_date=datetime.strptime(end, "%Y-%m-%d").date(),
            doctor_id=int(doctor_id) if doctor_id else None,
        )
        return success_response(
            data=AppointmentSerializer(queryset, many=True).data,
            message="Calendário de consultas obtido com sucesso.",
        )

    @action(detail=True, methods=["post"])
    def confirm(self, request, pk=None):
        try:
            appointment = AppointmentService.confirmar_consulta(int(pk), request.user, request=request)
        except Appointment.DoesNotExist:
            return error_response("Consulta não encontrada.", status=status.HTTP_404_NOT_FOUND)
        except ValueError as exc:
            return error_response(str(exc), status=status.HTTP_400_BAD_REQUEST)
        return success_response(
            data=AppointmentSerializer(appointment).data,
            message="Consulta confirmada com sucesso.",
        )

    @action(detail=True, methods=["post"])
    def start(self, request, pk=None):
        try:
            appointment = AppointmentService.iniciar_consulta(int(pk), request.user, request=request)
        except Appointment.DoesNotExist:
            return error_response("Consulta não encontrada.", status=status.HTTP_404_NOT_FOUND)
        except ValueError as exc:
            return error_response(str(exc), status=status.HTTP_400_BAD_REQUEST)
        return success_response(
            data=AppointmentSerializer(appointment).data,
            message="Consulta iniciada com sucesso.",
        )

    @extend_schema(
        request=ClinicalRecordPatchSerializer,
        responses={200: dict},
    )
    @action(detail=True, methods=["get", "patch"], url_path="clinical")
    def clinical_record(self, request, pk=None):
        if request.method == "GET":
            try:
                data = ClinicalRecordService.obter_prontuario(int(pk), request=request)
            except Appointment.DoesNotExist:
                return error_response("Consulta não encontrada.", status=status.HTTP_404_NOT_FOUND)
            return success_response(
                data=data,
                message="Prontuário clínico obtido com sucesso.",
            )
        return self._patch_clinical(request, pk)

    def _patch_clinical(self, request, pk):
        try:
            appointment = Appointment.objects.get(pk=pk)
        except Appointment.DoesNotExist:
            return error_response("Consulta não encontrada.", status=status.HTTP_404_NOT_FOUND)

        legacy_serializer = AppointmentClinicalUpdateSerializer(
            appointment,
            data=request.data,
            partial=True,
            context={"request": request},
        )
        legacy_serializer.is_valid(raise_exception=True)
        updated = legacy_serializer.save()

        soap_fields = ("subjetivo", "objetivo", "avaliacao", "plano")
        if any(f in request.data for f in soap_fields):
            try:
                ClinicalRecordService.guardar_soap(
                    int(pk),
                    request.user,
                    {f: request.data[f] for f in soap_fields if f in request.data},
                    request=request,
                )
            except ValueError as exc:
                return error_response(str(exc), status=status.HTTP_400_BAD_REQUEST)

        try:
            data = ClinicalRecordService.obter_prontuario(int(pk), request=request)
        except Appointment.DoesNotExist:
            data = AppointmentSerializer(updated).data
        else:
            pass

        return success_response(
            data=data,
            message="Prontuário clínico actualizado com sucesso.",
        )

    @extend_schema(request=SinaisVitaisSerializer)
    @action(detail=True, methods=["post"], url_path="vital-signs")
    def vital_signs(self, request, pk=None):
        serializer = SinaisVitaisSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            sinais = ClinicalRecordService.guardar_sinais_vitais(
                int(pk),
                request.user,
                serializer.validated_data,
                request=request,
            )
        except Appointment.DoesNotExist:
            return error_response("Consulta não encontrada.", status=status.HTTP_404_NOT_FOUND)
        except ValueError as exc:
            return error_response(str(exc), status=status.HTTP_400_BAD_REQUEST)
        data = ClinicalRecordService.obter_prontuario(int(pk), request=request)
        data["sinais_vitais"] = ClinicalRecordService._serialize_sinais(sinais)
        return success_response(
            data=data,
            message="Sinais vitais registados com sucesso.",
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(request=DiagnosticoCreateSerializer)
    @action(detail=True, methods=["post"], url_path="diagnoses")
    def diagnoses(self, request, pk=None):
        serializer = DiagnosticoCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            ClinicalRecordService.adicionar_diagnostico(
                int(pk),
                request.user,
                serializer.validated_data,
                request=request,
            )
        except Appointment.DoesNotExist:
            return error_response("Consulta não encontrada.", status=status.HTTP_404_NOT_FOUND)
        except ValueError as exc:
            return error_response(str(exc), status=status.HTTP_400_BAD_REQUEST)
        return success_response(
            data=ClinicalRecordService.obter_prontuario(int(pk), request=request),
            message="Diagnóstico adicionado com sucesso.",
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(request=PedidoExameSerializer)
    @action(detail=True, methods=["post"], url_path="laboratory")
    def laboratory(self, request, pk=None):
        serializer = PedidoExameSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            ClinicalRecordService.adicionar_pedido_laboratorio(
                int(pk),
                request.user,
                serializer.validated_data,
                request=request,
            )
        except Appointment.DoesNotExist:
            return error_response("Consulta não encontrada.", status=status.HTTP_404_NOT_FOUND)
        except ValueError as exc:
            return error_response(str(exc), status=status.HTTP_400_BAD_REQUEST)
        return success_response(
            data=ClinicalRecordService.obter_prontuario(int(pk), request=request),
            message="Pedido de laboratório registado com sucesso.",
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(request=PedidoExameSerializer)
    @action(detail=True, methods=["post"], url_path="imaging")
    def imaging(self, request, pk=None):
        serializer = PedidoExameSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            ClinicalRecordService.adicionar_pedido_imagiologia(
                int(pk),
                request.user,
                serializer.validated_data,
                request=request,
            )
        except Appointment.DoesNotExist:
            return error_response("Consulta não encontrada.", status=status.HTTP_404_NOT_FOUND)
        except ValueError as exc:
            return error_response(str(exc), status=status.HTTP_400_BAD_REQUEST)
        return success_response(
            data=ClinicalRecordService.obter_prontuario(int(pk), request=request),
            message="Pedido de imagiologia registado com sucesso.",
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(request=SeguimentoSerializer)
    @action(detail=True, methods=["post"], url_path="follow-up")
    def follow_up(self, request, pk=None):
        serializer = SeguimentoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            ClinicalRecordService.guardar_seguimento(
                int(pk),
                request.user,
                serializer.validated_data,
                request=request,
            )
        except Appointment.DoesNotExist:
            return error_response("Consulta não encontrada.", status=status.HTTP_404_NOT_FOUND)
        except ValueError as exc:
            return error_response(str(exc), status=status.HTTP_400_BAD_REQUEST)
        return success_response(
            data=ClinicalRecordService.obter_prontuario(int(pk), request=request),
            message="Seguimento agendado com sucesso.",
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(request=AppointmentClinicalUpdateSerializer)
    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        return self._finish(request, pk)

    @extend_schema(request=AppointmentCompleteSerializer)
    @action(detail=True, methods=["post"])
    def finish(self, request, pk=None):
        return self._finish(request, pk)

    def _finish(self, request, pk):
        serializer = AppointmentCompleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            appointment = AppointmentService.concluir_consulta(
                int(pk),
                request.user,
                diagnosis=serializer.validated_data.get("diagnosis", ""),
                clinical_notes=serializer.validated_data.get("clinical_notes", ""),
                request=request,
            )
        except Appointment.DoesNotExist:
            return error_response("Consulta não encontrada.", status=status.HTTP_404_NOT_FOUND)
        except ValueError as exc:
            return error_response(str(exc), status=status.HTTP_400_BAD_REQUEST)
        return success_response(
            data=AppointmentSerializer(appointment).data,
            message="Consulta concluída com sucesso.",
        )

    @extend_schema(request=AppointmentCancelSerializer)
    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        serializer = AppointmentCancelSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            appointment = AppointmentService.cancelar_consulta(
                int(pk),
                request.user,
                reason=serializer.validated_data.get("reason", ""),
                request=request,
            )
        except Appointment.DoesNotExist:
            return error_response("Consulta não encontrada.", status=status.HTTP_404_NOT_FOUND)
        except ValueError as exc:
            return error_response(str(exc), status=status.HTTP_400_BAD_REQUEST)
        return success_response(
            data=AppointmentSerializer(appointment).data,
            message="Consulta cancelada com sucesso.",
        )
