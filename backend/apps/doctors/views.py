"""Views do módulo Médicos."""

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.views import APIView

from apps.doctors.models import AltaMedica, EvolucaoClinica, Prescricao, SeguimentoClinico, Tratamento
from apps.doctors.permissions import (
    DISCHARGE_MAP,
    EVOLUTION_MAP,
    FOLLOWUP_MAP,
    PRESCRIPTION_MAP,
    TREATMENT_MAP,
    DoctorsPermissionMixin,
)
from apps.doctors.serializers import (
    AltaMedicaSerializer,
    EvolucaoClinicaSerializer,
    PrescricaoCreateSerializer,
    PrescricaoSerializer,
    SeguimentoClinicoSerializer,
    TratamentoSerializer,
)
from apps.doctors.services.clinical_evolution_service import ClinicalEvolutionService
from apps.doctors.services.discharge_service import DischargeService
from apps.doctors.services.followup_service import FollowupService
from apps.doctors.services.prescription_service import PrescriptionService
from apps.doctors.services.treatment_service import TreatmentService
from core.pagination import StandardPagination
from core.responses import error_response, success_response


class DoctorsModelViewSet(DoctorsPermissionMixin, viewsets.ModelViewSet):
    pagination_class = StandardPagination
    http_method_names = ["get", "post", "patch", "head", "options"]

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
            message="Registos obtidos com sucesso.",
        )

    def retrieve(self, request, *args, **kwargs):
        return success_response(data=self.get_serializer(self.get_object()).data)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(data=serializer.data, message="Registo actualizado.")


@extend_schema_view(
    list=extend_schema(tags=["Prescrições"]),
    retrieve=extend_schema(tags=["Prescrições"]),
    create=extend_schema(tags=["Prescrições"]),
    partial_update=extend_schema(tags=["Prescrições"]),
)
class PrescricaoViewSet(DoctorsModelViewSet):
    queryset = Prescricao.objects.select_related("paciente", "medico", "consulta").prefetch_related(
        "medicamentos", "planos"
    )
    serializer_class = PrescricaoSerializer
    permission_map = PRESCRIPTION_MAP

    def create(self, request, *args, **kwargs):
        serializer = PrescricaoCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        medicamentos = data.pop("medicamentos", [])
        plano = data.pop("plano", None)
        prescricao = PrescriptionService.criar_prescricao(
            consulta_id=data["consulta_id"],
            medico=request.user,
            data={
                "observacoes": data.get("observacoes", ""),
                "medicamentos": medicamentos,
                "plano": plano,
            },
            request=request,
        )
        return success_response(
            data=PrescricaoSerializer(prescricao).data,
            message="Prescrição criada com sucesso.",
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        prescricao = PrescriptionService.aprovar_prescricao(int(pk), request.user, request=request)
        return success_response(data=PrescricaoSerializer(prescricao).data, message="Prescrição aprovada.")

    @action(detail=True, methods=["post"])
    def finish(self, request, pk=None):
        prescricao = PrescriptionService.concluir_prescricao(int(pk), request.user, request=request)
        return success_response(data=PrescricaoSerializer(prescricao).data, message="Prescrição concluída.")

    @action(detail=False, methods=["get"])
    def history(self, request):
        paciente_id = request.query_params.get("paciente_id")
        if not paciente_id:
            return error_response("Parâmetro paciente_id é obrigatório.")
        data = PrescriptionService.historico_paciente(int(paciente_id))
        return success_response(data=data, message="Histórico terapêutico obtido.")


@extend_schema_view(
    list=extend_schema(tags=["Tratamentos"]),
    retrieve=extend_schema(tags=["Tratamentos"]),
    create=extend_schema(tags=["Tratamentos"]),
)
class TratamentoViewSet(DoctorsModelViewSet):
    queryset = Tratamento.objects.select_related("paciente", "consulta", "responsavel")
    serializer_class = TratamentoSerializer
    permission_map = TREATMENT_MAP

    def create(self, request, *args, **kwargs):
        consulta_id = request.data.get("consulta_id")
        if not consulta_id:
            return error_response("consulta_id é obrigatório.")
        payload = {k: v for k, v in request.data.items() if k != "consulta_id"}
        tratamento = TreatmentService.criar_tratamento(
            consulta_id=int(consulta_id),
            user=request.user,
            data=payload,
            request=request,
        )
        return success_response(
            data=TratamentoSerializer(tratamento).data,
            message="Tratamento criado.",
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["post"])
    def finish(self, request, pk=None):
        tratamento = TreatmentService.concluir_tratamento(int(pk), request.user, request=request)
        return success_response(data=TratamentoSerializer(tratamento).data, message="Tratamento concluído.")


class EvolucaoViewSet(DoctorsModelViewSet):
    queryset = EvolucaoClinica.objects.select_related("paciente", "consulta")
    serializer_class = EvolucaoClinicaSerializer
    permission_map = EVOLUTION_MAP

    def create(self, request, *args, **kwargs):
        consulta_id = request.data.get("consulta_id")
        if not consulta_id:
            return error_response("consulta_id é obrigatório.")
        payload = {k: v for k, v in request.data.items() if k != "consulta_id"}
        evolucao = ClinicalEvolutionService.registar_evolucao(
            consulta_id=int(consulta_id),
            user=request.user,
            data=payload,
            request=request,
        )
        return success_response(
            data=EvolucaoClinicaSerializer(evolucao).data,
            message="Evolução registada.",
            status=status.HTTP_201_CREATED,
        )


class AltaViewSet(DoctorsModelViewSet):
    queryset = AltaMedica.objects.select_related("paciente", "consulta", "medico")
    serializer_class = AltaMedicaSerializer
    permission_map = DISCHARGE_MAP

    def create(self, request, *args, **kwargs):
        consulta_id = request.data.get("consulta_id")
        if not consulta_id:
            return error_response("consulta_id é obrigatório.")
        payload = {k: v for k, v in request.data.items() if k != "consulta_id"}
        alta = DischargeService.emitir_alta(
            consulta_id=int(consulta_id),
            medico=request.user,
            data=payload,
            request=request,
        )
        return success_response(
            data=AltaMedicaSerializer(alta).data,
            message="Alta médica emitida.",
            status=status.HTTP_201_CREATED,
        )


class SeguimentoViewSet(DoctorsModelViewSet):
    queryset = SeguimentoClinico.objects.select_related(
        "paciente", "consulta_origem", "consulta_agendada", "medico"
    )
    serializer_class = SeguimentoClinicoSerializer
    permission_map = FOLLOWUP_MAP

    def create(self, request, *args, **kwargs):
        consulta_id = request.data.get("consulta_id")
        if not consulta_id:
            return error_response("consulta_id é obrigatório.")
        payload = {k: v for k, v in request.data.items() if k != "consulta_id"}
        seguimento = FollowupService.agendar_seguimento(
            consulta_id=int(consulta_id),
            medico=request.user,
            data=payload,
            request=request,
        )
        return success_response(
            data=SeguimentoClinicoSerializer(seguimento).data,
            message="Seguimento agendado.",
            status=status.HTTP_201_CREATED,
        )
