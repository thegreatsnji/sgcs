"""Views do módulo de laboratório."""

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action

from apps.laboratory.filters import PedidoLaboratorialFilter
from apps.laboratory.models import PedidoLaboratorial
from apps.laboratory.permissions import LaboratoryPermissionMixin
from apps.laboratory.serializers import (
    PedidoLaboratorialSerializer,
    PedidoLaboratorialUpdateSerializer,
)
from apps.laboratory.services.laboratory_service import LaboratoryService
from core.pagination import StandardPagination
from core.responses import error_response, success_response


@extend_schema_view(
    list=extend_schema(tags=["Laboratório"]),
    retrieve=extend_schema(tags=["Laboratório"]),
    partial_update=extend_schema(tags=["Laboratório"]),
    pending=extend_schema(tags=["Laboratório"]),
    today=extend_schema(tags=["Laboratório"]),
    collection_queue=extend_schema(tags=["Laboratório"]),
    receive=extend_schema(tags=["Laboratório"]),
    collect=extend_schema(tags=["Laboratório"]),
    start=extend_schema(tags=["Laboratório"]),
    finish=extend_schema(tags=["Laboratório"]),
)
class LaboratoryViewSet(LaboratoryPermissionMixin, viewsets.ModelViewSet):
    queryset = (
        PedidoLaboratorial.objects.select_related(
            "paciente",
            "medico",
            "consulta",
            "pedido_consulta",
            "pedido_consulta__servico",
        )
        .prefetch_related("exames", "resultado")
        .order_by("-data_pedido")
    )
    serializer_class = PedidoLaboratorialSerializer
    pagination_class = StandardPagination
    filterset_class = PedidoLaboratorialFilter
    http_method_names = ["get", "patch", "post", "head", "options"]

    def get_serializer_class(self):
        if self.action in {"partial_update", "update"}:
            return PedidoLaboratorialUpdateSerializer
        return PedidoLaboratorialSerializer

    def _paginated(self, queryset, message: str):
        page = self.paginate_queryset(queryset)
        serializer = PedidoLaboratorialSerializer(page, many=True)
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
        from apps.laboratory.ordering import priority_order_case

        queryset = self.filter_queryset(
            self.get_queryset().annotate(_prio=priority_order_case()).order_by("_prio", "-data_pedido")
        )
        return self._paginated(queryset, "Pedidos laboratoriais obtidos com sucesso.")

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        return success_response(
            data=PedidoLaboratorialSerializer(instance).data,
            message="Pedido laboratorial obtido com sucesso.",
        )

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = PedidoLaboratorialUpdateSerializer(
            instance,
            data=request.data,
            partial=True,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        updated = serializer.save()
        return success_response(
            data=PedidoLaboratorialSerializer(updated).data,
            message="Pedido actualizado com sucesso.",
        )

    @action(detail=False, methods=["get"], url_path="pending")
    def pending(self, request):
        queryset = self.filter_queryset(LaboratoryService.listar_pendentes())
        return self._paginated(queryset, "Pedidos pendentes obtidos com sucesso.")

    @action(detail=False, methods=["get"], url_path="today")
    def today(self, request):
        queryset = self.filter_queryset(LaboratoryService.listar_do_dia())
        return self._paginated(queryset, "Pedidos do dia obtidos com sucesso.")

    @action(detail=False, methods=["get"], url_path="collection-queue")
    def collection_queue(self, request):
        queryset = self.filter_queryset(LaboratoryService.fila_colheitas())
        return self._paginated(queryset, "Fila de colheitas obtida com sucesso.")

    @action(detail=True, methods=["post"])
    def receive(self, request, pk=None):
        try:
            pedido = LaboratoryService.receber_pedido(int(pk), request.user, request=request)
        except PedidoLaboratorial.DoesNotExist:
            return error_response("Pedido não encontrado.", status=status.HTTP_404_NOT_FOUND)
        except ValueError as exc:
            return error_response(str(exc), status=status.HTTP_400_BAD_REQUEST)
        return success_response(
            data=PedidoLaboratorialSerializer(pedido).data,
            message="Pedido recebido com sucesso.",
        )

    @action(detail=True, methods=["post"])
    def collect(self, request, pk=None):
        try:
            pedido = LaboratoryService.registar_colheita(int(pk), request.user, request=request)
        except PedidoLaboratorial.DoesNotExist:
            return error_response("Pedido não encontrado.", status=status.HTTP_404_NOT_FOUND)
        except ValueError as exc:
            return error_response(str(exc), status=status.HTTP_400_BAD_REQUEST)
        return success_response(
            data=PedidoLaboratorialSerializer(pedido).data,
            message="Colheita registada com sucesso.",
        )

    @action(detail=True, methods=["post"])
    def start(self, request, pk=None):
        try:
            pedido = LaboratoryService.iniciar_processamento(int(pk), request.user, request=request)
        except PedidoLaboratorial.DoesNotExist:
            return error_response("Pedido não encontrado.", status=status.HTTP_404_NOT_FOUND)
        except ValueError as exc:
            return error_response(str(exc), status=status.HTTP_400_BAD_REQUEST)
        return success_response(
            data=PedidoLaboratorialSerializer(pedido).data,
            message="Processamento iniciado com sucesso.",
        )

    @action(detail=True, methods=["post"])
    def finish(self, request, pk=None):
        try:
            pedido = LaboratoryService.concluir_exame(int(pk), request.user, request=request)
        except PedidoLaboratorial.DoesNotExist:
            return error_response("Pedido não encontrado.", status=status.HTTP_404_NOT_FOUND)
        except ValueError as exc:
            return error_response(str(exc), status=status.HTTP_400_BAD_REQUEST)
        return success_response(
            data=PedidoLaboratorialSerializer(pedido).data,
            message="Exame concluído com sucesso.",
        )
