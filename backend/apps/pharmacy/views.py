from datetime import date, timedelta

from django.db.models import F, Q
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.views import APIView

from apps.appointments.models import Appointment
from apps.patients.models import Patient
from apps.pharmacy.constants import TipoMovimentoStockUrgencia
from apps.pharmacy.models import MedicamentoUrgencia, MovimentoStockUrgencia
from apps.pharmacy.permissions import (
    ADJUST_CODES,
    CREATE_CODES,
    EDIT_CODES,
    ENTRY_CODES,
    EXIT_CODES,
    HISTORY_CODES,
    VIEW_CODES,
    require_any,
)
from apps.pharmacy.serializers import (
    MedicamentoUrgenciaSerializer,
    MedicamentoUrgenciaWriteSerializer,
    MovimentoStockUrgenciaSerializer,
    RegistarMovimentoSerializer,
)
from apps.pharmacy.services.stock_service import StockUrgenciaError, StockUrgenciaService
from apps.pharmacy.status import dias_proxima_validade
from core.pagination import StandardPagination
from core.responses import error_response, success_response


def _load_optional_patient(pk):
    if not pk:
        return None
    return Patient.objects.filter(pk=pk).first()


def _load_optional_appointment(pk):
    if not pk:
        return None
    return Appointment.objects.filter(pk=pk).first()


@extend_schema_view(
    list=extend_schema(tags=["Stock de urgência"]),
    retrieve=extend_schema(tags=["Stock de urgência"]),
    create=extend_schema(tags=["Stock de urgência"]),
    partial_update=extend_schema(tags=["Stock de urgência"]),
)
class MedicamentoUrgenciaViewSet(viewsets.ModelViewSet):
    queryset = MedicamentoUrgencia.objects.select_related("servico").all()
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["activo", "categoria"]
    search_fields = ["codigo", "nome", "forma_apresentacao"]
    ordering_fields = ["nome", "quantidade_stock", "updated_at"]
    http_method_names = ["get", "post", "patch", "head", "options"]

    def get_permissions(self):
        if self.action == "create":
            return [require_any(*CREATE_CODES)()]
        if self.action in ("update", "partial_update"):
            return [require_any(*EDIT_CODES)()]
        if self.action in ("entrada", "movimento") and self.request.data.get("tipo") == "ENTRADA":
            return [require_any(*ENTRY_CODES)()]
        if self.action == "entrada":
            return [require_any(*ENTRY_CODES)()]
        if self.action == "saida":
            return [require_any(*EXIT_CODES)()]
        if self.action in ("ajuste", "perda"):
            return [require_any(*ADJUST_CODES)()]
        if self.action == "movimento":
            tipo = (self.request.data or {}).get("tipo")
            if tipo == TipoMovimentoStockUrgencia.SAIDA:
                return [require_any(*EXIT_CODES)()]
            if tipo == TipoMovimentoStockUrgencia.AJUSTE:
                return [require_any(*ADJUST_CODES)()]
            if tipo == TipoMovimentoStockUrgencia.PERDA_EXPIRACAO:
                return [require_any(*ADJUST_CODES)()]
            return [require_any(*ENTRY_CODES)()]
        return [require_any(*VIEW_CODES)()]

    def get_serializer_class(self):
        if self.action in ("create", "partial_update"):
            return MedicamentoUrgenciaWriteSerializer
        return MedicamentoUrgenciaSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        abaixo = self.request.query_params.get("abaixo_minimo")
        if abaixo in ("1", "true", "True"):
            qs = qs.filter(quantidade_stock__lte=F("stock_minimo"))
        estado = self.request.query_params.get("estado")
        hoje = date.today()
        limite = hoje + timedelta(days=dias_proxima_validade())
        if estado == "SEM_STOCK":
            qs = qs.filter(quantidade_stock=0)
        elif estado == "STOCK_BAIXO":
            qs = qs.filter(quantidade_stock__gt=0, quantidade_stock__lte=F("stock_minimo"))
        elif estado == "EXPIRADO":
            qs = qs.filter(validade__lt=hoje)
        elif estado == "PROXIMO_DA_VALIDADE":
            qs = qs.filter(validade__gte=hoje, validade__lte=limite)
        elif estado == "DISPONIVEL":
            qs = qs.filter(quantidade_stock__gt=F("stock_minimo")).filter(
                Q(validade__isnull=True) | Q(validade__gt=limite)
            )
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
            message="Stock de urgência obtido com sucesso.",
        )

    def retrieve(self, request, *args, **kwargs):
        return success_response(
            data=MedicamentoUrgenciaSerializer(self.get_object()).data,
            message="Item obtido com sucesso.",
        )

    def create(self, request, *args, **kwargs):
        serializer = MedicamentoUrgenciaWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            obj = StockUrgenciaService.criar_item(
                nome=data["nome"],
                categoria=data.get("categoria") or "MEDICAMENTO",
                unidade=data.get("unidade") or "unidade",
                quantidade_inicial=data.get("quantidade_inicial") or 0,
                forma_apresentacao=data.get("forma_apresentacao") or "",
                stock_minimo=data.get("stock_minimo") or 5,
                validade=data.get("validade"),
                preco_referencia_fcfa=data.get("preco_referencia_fcfa"),
                observacoes=data.get("observacoes") or "",
                quantidade_texto_original=data.get("quantidade_texto_original") or "",
                operador=request.user,
                request=request,
            )
        except StockUrgenciaError as exc:
            return error_response(message=str(exc), status=status.HTTP_400_BAD_REQUEST)
        return success_response(
            data=MedicamentoUrgenciaSerializer(obj).data,
            message="Item registado com sucesso.",
            status=status.HTTP_201_CREATED,
        )

    def partial_update(self, request, *args, **kwargs):
        obj = self.get_object()
        serializer = MedicamentoUrgenciaWriteSerializer(obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        data = dict(serializer.validated_data)
        data.pop("quantidade_inicial", None)
        if "quantidade_stock" in data:
            data.pop("quantidade_stock")
        for attr, value in data.items():
            setattr(obj, attr, value)
        obj.save()
        return success_response(
            data=MedicamentoUrgenciaSerializer(obj).data,
            message="Item actualizado com sucesso.",
        )

    def _move(self, request, tipo: str | None = None):
        medicamento = self.get_object()
        payload = RegistarMovimentoSerializer(data=request.data)
        payload.is_valid(raise_exception=True)
        tipo = tipo or payload.validated_data.get("tipo")
        if not tipo:
            return error_response(message="Indique o tipo de movimento.", status=status.HTTP_400_BAD_REQUEST)
        try:
            mov = StockUrgenciaService.registar_movimento(
                medicamento,
                tipo=tipo,
                quantidade=payload.validated_data["quantidade"],
                motivo=payload.validated_data.get("motivo", ""),
                operador=request.user,
                paciente=_load_optional_patient(payload.validated_data.get("paciente")),
                consulta=_load_optional_appointment(payload.validated_data.get("consulta")),
                request=request,
            )
        except StockUrgenciaError as exc:
            return error_response(message=str(exc), status=status.HTTP_400_BAD_REQUEST)
        medicamento.refresh_from_db()
        return success_response(
            data={
                "item": MedicamentoUrgenciaSerializer(medicamento).data,
                "medicamento": MedicamentoUrgenciaSerializer(medicamento).data,
                "movimento": MovimentoStockUrgenciaSerializer(mov).data,
            },
            message="Movimento registado com sucesso.",
        )

    @extend_schema(tags=["Stock de urgência"], request=RegistarMovimentoSerializer)
    @action(detail=True, methods=["post"], url_path="movimento")
    def movimento(self, request, pk=None):
        return self._move(request)

    @action(detail=True, methods=["post"], url_path="entrada")
    def entrada(self, request, pk=None):
        return self._move(request, tipo=TipoMovimentoStockUrgencia.ENTRADA)

    @action(detail=True, methods=["post"], url_path="saida")
    def saida(self, request, pk=None):
        return self._move(request, tipo=TipoMovimentoStockUrgencia.SAIDA)

    @action(detail=True, methods=["post"], url_path="ajuste")
    def ajuste(self, request, pk=None):
        return self._move(request, tipo=TipoMovimentoStockUrgencia.AJUSTE)

    @action(detail=True, methods=["post"], url_path="perda")
    def perda(self, request, pk=None):
        return self._move(request, tipo=TipoMovimentoStockUrgencia.PERDA_EXPIRACAO)


@extend_schema_view(list=extend_schema(tags=["Stock de urgência"]))
class MovimentoStockUrgenciaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MovimentoStockUrgencia.objects.select_related("medicamento", "operador", "paciente")
    serializer_class = MovimentoStockUrgenciaSerializer
    pagination_class = StandardPagination
    filterset_fields = ["medicamento", "tipo", "operador"]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    search_fields = ["medicamento__nome", "motivo"]
    ordering = ["-created_at"]
    http_method_names = ["get", "head", "options"]

    def get_permissions(self):
        return [require_any(*HISTORY_CODES)()]

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


class StockDashboardView(APIView):
    permission_classes = [require_any(*VIEW_CODES)]

    def get(self, request):
        qs = MedicamentoUrgencia.objects.filter(activo=True)
        hoje = date.today()
        limite = hoje + timedelta(days=dias_proxima_validade())
        baixo = qs.filter(quantidade_stock__gt=0, quantidade_stock__lte=F("stock_minimo"))
        sem = qs.filter(quantidade_stock=0)
        expirado = qs.filter(validade__lt=hoje)
        proximo = qs.filter(validade__gte=hoje, validade__lte=limite)
        atencao = list(
            qs.filter(
                Q(quantidade_stock__lte=F("stock_minimo")) | Q(validade__lte=limite, validade__isnull=False)
            ).order_by("quantidade_stock", "nome")[:8]
        )
        return success_response(
            data={
                "total_itens": qs.count(),
                "stock_baixo": baixo.count(),
                "sem_stock": sem.count(),
                "proximos_validade": proximo.count(),
                "expirados": expirado.count(),
                "precisa_atencao": MedicamentoUrgenciaSerializer(atencao, many=True).data,
            },
            message="Resumo do stock de urgência.",
        )
