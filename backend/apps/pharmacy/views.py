from django.db.models import F
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action

from apps.pharmacy.models import MedicamentoUrgencia, MovimentoStockUrgencia
from apps.pharmacy.serializers import (
    MedicamentoUrgenciaSerializer,
    MedicamentoUrgenciaWriteSerializer,
    MovimentoStockUrgenciaSerializer,
    RegistarMovimentoSerializer,
)
from apps.pharmacy.services.stock_service import StockUrgenciaError, StockUrgenciaService
from apps.users.permissions import require_permission
from core.pagination import StandardPagination
from core.responses import error_response, success_response


class PharmacyPermissionMixin:
    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "movimento"):
            return [require_permission("pharmacy.edit")()]
        if self.action == "destroy":
            return [require_permission("pharmacy.delete")()]
        return [require_permission("pharmacy.view")()]


@extend_schema_view(
    list=extend_schema(tags=["Farmácia — Urgência"]),
    retrieve=extend_schema(tags=["Farmácia — Urgência"]),
    create=extend_schema(tags=["Farmácia — Urgência"]),
    partial_update=extend_schema(tags=["Farmácia — Urgência"]),
)
class MedicamentoUrgenciaViewSet(PharmacyPermissionMixin, viewsets.ModelViewSet):
    queryset = MedicamentoUrgencia.objects.select_related("servico").all()
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["activo"]
    search_fields = ["codigo", "nome"]
    ordering_fields = ["nome", "quantidade_stock", "updated_at"]
    http_method_names = ["get", "post", "patch", "head", "options"]

    def get_serializer_class(self):
        if self.action in ("create", "partial_update"):
            return MedicamentoUrgenciaWriteSerializer
        return MedicamentoUrgenciaSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        abaixo = self.request.query_params.get("abaixo_minimo")
        if abaixo in ("1", "true", "True"):
            qs = qs.filter(quantidade_stock__lte=F("stock_minimo"))
        return qs

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = MedicamentoUrgenciaSerializer(page, many=True)
        paginated = self.get_paginated_response(serializer.data)
        return success_response(
            data={
                "count": paginated.data["count"],
                "next": paginated.data["next"],
                "previous": paginated.data["previous"],
                "results": paginated.data["results"],
            },
            message="Medicamentos de urgência obtidos com sucesso.",
        )

    def retrieve(self, request, *args, **kwargs):
        return success_response(
            data=MedicamentoUrgenciaSerializer(self.get_object()).data,
            message="Medicamento obtido com sucesso.",
        )

    def create(self, request, *args, **kwargs):
        serializer = MedicamentoUrgenciaWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = MedicamentoUrgencia.objects.create(**serializer.validated_data)
        return success_response(
            data=MedicamentoUrgenciaSerializer(obj).data,
            message="Medicamento registado com sucesso.",
            status_code=status.HTTP_201_CREATED,
        )

    def partial_update(self, request, *args, **kwargs):
        obj = self.get_object()
        serializer = MedicamentoUrgenciaWriteSerializer(obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        for attr, value in serializer.validated_data.items():
            setattr(obj, attr, value)
        obj.save()
        return success_response(
            data=MedicamentoUrgenciaSerializer(obj).data,
            message="Medicamento actualizado com sucesso.",
        )

    @extend_schema(tags=["Farmácia — Urgência"], request=RegistarMovimentoSerializer)
    @action(detail=True, methods=["post"], url_path="movimento")
    def movimento(self, request, pk=None):
        medicamento = self.get_object()
        payload = RegistarMovimentoSerializer(data=request.data)
        payload.is_valid(raise_exception=True)
        try:
            mov = StockUrgenciaService.registar_movimento(
                medicamento,
                tipo=payload.validated_data["tipo"],
                quantidade=payload.validated_data["quantidade"],
                motivo=payload.validated_data.get("motivo", ""),
                operador=request.user,
            )
        except StockUrgenciaError as exc:
            return error_response(message=str(exc), status_code=status.HTTP_400_BAD_REQUEST)
        medicamento.refresh_from_db()
        return success_response(
            data={
                "medicamento": MedicamentoUrgenciaSerializer(medicamento).data,
                "movimento": MovimentoStockUrgenciaSerializer(mov).data,
            },
            message="Movimento registado com sucesso.",
        )


@extend_schema_view(list=extend_schema(tags=["Farmácia — Urgência"]))
class MovimentoStockUrgenciaViewSet(PharmacyPermissionMixin, viewsets.ReadOnlyModelViewSet):
    queryset = MovimentoStockUrgencia.objects.select_related("medicamento", "operador")
    serializer_class = MovimentoStockUrgenciaSerializer
    pagination_class = StandardPagination
    filterset_fields = ["medicamento", "tipo"]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering = ["-created_at"]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = MovimentoStockUrgenciaSerializer(page, many=True)
        paginated = self.get_paginated_response(serializer.data)
        return success_response(
            data={
                "count": paginated.data["count"],
                "next": paginated.data["next"],
                "previous": paginated.data["previous"],
                "results": paginated.data["results"],
            },
            message="Movimentos obtidos com sucesso.",
        )
