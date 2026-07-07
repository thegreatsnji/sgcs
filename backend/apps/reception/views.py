"""Views do módulo de receção."""

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.views import APIView

from apps.reception.filters import ReceptionHistoryFilter, WaitingQueueFilter
from apps.reception.models import ReceptionCheckIn, Referral, WaitingQueue
from apps.reception.permissions import ReceptionPermissionMixin
from apps.reception.serializers import (
    AssignToDoctorSerializer,
    CheckInCreateSerializer,
    ReceptionCheckInSerializer,
    ReferralCreateSerializer,
    ReferralSerializer,
    WaitingQueueSerializer,
    WaitingQueueUpdateSerializer,
)
from apps.reception.services.reception_service import ReceptionService
from core.pagination import StandardPagination
from core.responses import error_response, success_response


@extend_schema_view(
    check_in=extend_schema(tags=["Receção"]),
    queue=extend_schema(tags=["Receção"]),
    update_queue=extend_schema(tags=["Receção"]),
    assign_to_doctor=extend_schema(tags=["Receção"]),
    history=extend_schema(tags=["Receção"]),
    create_referral=extend_schema(tags=["Receção"]),
)
class ReceptionViewSet(ReceptionPermissionMixin, viewsets.GenericViewSet):
    pagination_class = StandardPagination
    filterset_class = WaitingQueueFilter

    @extend_schema(request=CheckInCreateSerializer, tags=["Receção"])
    @action(detail=False, methods=["post"], url_path="check-in")
    def check_in(self, request):
        serializer = CheckInCreateSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        check_in = serializer.save()
        data = ReceptionCheckInSerializer(check_in).data
        queue_entry = WaitingQueueSerializer(check_in.queue_entry).data
        return success_response(
            data={"check_in": data, "queue_entry": queue_entry},
            message="Check-in efectuado com sucesso.",
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=["get"], url_path="queue")
    def queue(self, request):
        queryset = ReceptionService.get_active_queue(use_cache=True)
        if hasattr(queryset, "filter"):
            filterset = WaitingQueueFilter(request.query_params, queryset=queryset)
            queryset = filterset.qs
        page = self.paginate_queryset(queryset)
        serializer = WaitingQueueSerializer(page, many=True)
        paginated = self.get_paginated_response(serializer.data)
        return success_response(
            data={
                "count": paginated.data["count"],
                "next": paginated.data["next"],
                "previous": paginated.data["previous"],
                "results": paginated.data["results"],
            },
            message="Fila de espera obtida com sucesso.",
        )

    @extend_schema(request=WaitingQueueUpdateSerializer, tags=["Receção"])
    @action(detail=False, methods=["patch"], url_path=r"queue/(?P<queue_id>\d+)")
    def update_queue(self, request, queue_id=None):
        try:
            entry = WaitingQueue.objects.get(pk=queue_id)
        except WaitingQueue.DoesNotExist:
            return error_response("Registo não encontrado.", status=status.HTTP_404_NOT_FOUND)
        serializer = WaitingQueueUpdateSerializer(
            entry,
            data=request.data,
            partial=True,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        updated = serializer.save()
        return success_response(
            data=WaitingQueueSerializer(updated).data,
            message="Fila actualizada com sucesso.",
        )

    @extend_schema(request=AssignToDoctorSerializer, tags=["Receção"])
    @action(detail=False, methods=["post"], url_path="assign-to-doctor")
    def assign_to_doctor(self, request):
        serializer = AssignToDoctorSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        referral = serializer.save()
        queue_entry = WaitingQueue.objects.filter(check_in=referral.check_in).first()
        return success_response(
            data={
                "referral": ReferralSerializer(referral).data,
                "queue_entry": WaitingQueueSerializer(queue_entry).data if queue_entry else None,
            },
            message="Paciente encaminhado para médico com sucesso.",
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=["get"], url_path="history")
    def history(self, request):
        queryset = ReceptionCheckIn.objects.select_related("patient", "receptionist").order_by(
            "-check_in_time"
        )
        filterset = ReceptionHistoryFilter(request.query_params, queryset=queryset)
        queryset = filterset.qs
        page = self.paginate_queryset(queryset)
        serializer = ReceptionCheckInSerializer(page, many=True)
        paginated = self.get_paginated_response(serializer.data)
        return success_response(
            data={
                "count": paginated.data["count"],
                "next": paginated.data["next"],
                "previous": paginated.data["previous"],
                "results": paginated.data["results"],
            },
            message="Histórico obtido com sucesso.",
        )

    @extend_schema(request=ReferralCreateSerializer, tags=["Receção"])
    @action(detail=False, methods=["post"], url_path="referrals")
    def create_referral(self, request):
        serializer = ReferralCreateSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        referral = serializer.save()
        return success_response(
            data=ReferralSerializer(referral).data,
            message="Encaminhamento registado com sucesso.",
            status=status.HTTP_201_CREATED,
        )
