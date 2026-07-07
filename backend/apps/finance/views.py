"""Views do módulo financeiro."""

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.views import APIView

from apps.finance.filters import CaixaFilter, DespesaFilter, MovimentoFilter
from apps.finance.models import Caixa, CategoriaFinanceira, Despesa, MovimentoFinanceiro
from apps.finance.permissions import (
    CATEGORY_MAP,
    CASH_REGISTER_MAP,
    EXPENSE_MAP,
    MOVEMENT_MAP,
    REPORT_MAP,
    FinancePermissionMixin,
)
from apps.finance.serializers import (
    CaixaSerializer,
    CategoriaFinanceiraSerializer,
    DespesaCreateSerializer,
    DespesaSerializer,
    MovimentoFinanceiroSerializer,
)
from apps.finance.services.finance_service import FinanceService
from apps.users.permissions import HasModulePermission
from core.pagination import StandardPagination
from core.responses import error_response, success_response


class CashRegisterPermissionMixin(FinancePermissionMixin):
    permission_map = CASH_REGISTER_MAP


class MovementPermissionMixin(FinancePermissionMixin):
    permission_map = MOVEMENT_MAP


class ExpensePermissionMixin(FinancePermissionMixin):
    permission_map = EXPENSE_MAP


class CategoryPermissionMixin(FinancePermissionMixin):
    permission_map = CATEGORY_MAP


@extend_schema_view(
    list=extend_schema(tags=["Financeiro — Caixas"]),
    retrieve=extend_schema(tags=["Financeiro — Caixas"]),
    create=extend_schema(tags=["Financeiro — Caixas"]),
    partial_update=extend_schema(tags=["Financeiro — Caixas"]),
)
class CaixaViewSet(CashRegisterPermissionMixin, viewsets.ModelViewSet):
    queryset = Caixa.objects.all()
    serializer_class = CaixaSerializer
    pagination_class = StandardPagination
    filterset_class = CaixaFilter
    http_method_names = ["get", "post", "patch", "head", "options"]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = CaixaSerializer(page, many=True)
        paginated = self.get_paginated_response(serializer.data)
        return success_response(
            data={
                "count": paginated.data["count"],
                "next": paginated.data["next"],
                "previous": paginated.data["previous"],
                "results": paginated.data["results"],
            },
            message="Caixas obtidas com sucesso.",
        )

    def retrieve(self, request, *args, **kwargs):
        return success_response(
            data=CaixaSerializer(self.get_object()).data,
            message="Caixa obtida com sucesso.",
        )

    def create(self, request, *args, **kwargs):
        serializer = CaixaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(
            data=serializer.data,
            message="Caixa criada com sucesso.",
            status=status.HTTP_201_CREATED,
        )

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = CaixaSerializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(data=serializer.data, message="Caixa actualizada com sucesso.")

    @action(detail=True, methods=["post"])
    def open(self, request, pk=None):
        from decimal import Decimal

        saldo = Decimal(str(request.data.get("saldo_inicial", 0)))
        try:
            caixa = FinanceService.abrir_caixa(
                int(pk),
                request.user,
                saldo_inicial=saldo,
                observacoes=request.data.get("observacoes", ""),
                request=request,
            )
        except Caixa.DoesNotExist:
            return error_response("Caixa não encontrada.", status=status.HTTP_404_NOT_FOUND)
        except ValueError as exc:
            return error_response(str(exc), status=status.HTTP_400_BAD_REQUEST)
        return success_response(data=CaixaSerializer(caixa).data, message="Caixa aberta com sucesso.")

    @action(detail=True, methods=["post"])
    def close(self, request, pk=None):
        try:
            caixa = FinanceService.fechar_caixa(
                int(pk),
                request.user,
                observacoes=request.data.get("observacoes", ""),
                request=request,
            )
        except Caixa.DoesNotExist:
            return error_response("Caixa não encontrada.", status=status.HTTP_404_NOT_FOUND)
        except ValueError as exc:
            return error_response(str(exc), status=status.HTTP_400_BAD_REQUEST)
        return success_response(data=CaixaSerializer(caixa).data, message="Caixa fechada com sucesso.")

    @action(detail=True, methods=["get"])
    def history(self, request, pk=None):
        try:
            data = FinanceService.historico_caixa(int(pk))
        except Caixa.DoesNotExist:
            return error_response("Caixa não encontrada.", status=status.HTTP_404_NOT_FOUND)
        return success_response(data=data, message="Histórico obtido com sucesso.")


@extend_schema_view(
    list=extend_schema(tags=["Financeiro — Movimentos"]),
    retrieve=extend_schema(tags=["Financeiro — Movimentos"]),
)
class MovimentoViewSet(MovementPermissionMixin, viewsets.ReadOnlyModelViewSet):
    queryset = MovimentoFinanceiro.objects.select_related("caixa", "utilizador")
    serializer_class = MovimentoFinanceiroSerializer
    pagination_class = StandardPagination
    filterset_class = MovimentoFilter

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = MovimentoFinanceiroSerializer(page, many=True)
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


@extend_schema_view(
    list=extend_schema(tags=["Financeiro — Despesas"]),
    retrieve=extend_schema(tags=["Financeiro — Despesas"]),
    create=extend_schema(tags=["Financeiro — Despesas"]),
    partial_update=extend_schema(tags=["Financeiro — Despesas"]),
)
class DespesaViewSet(ExpensePermissionMixin, viewsets.ModelViewSet):
    queryset = Despesa.objects.select_related("criado_por", "categoria_financeira")
    serializer_class = DespesaSerializer
    pagination_class = StandardPagination
    filterset_class = DespesaFilter
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_serializer_class(self):
        if self.action == "create":
            return DespesaCreateSerializer
        return DespesaSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = DespesaSerializer(page, many=True)
        paginated = self.get_paginated_response(serializer.data)
        return success_response(
            data={
                "count": paginated.data["count"],
                "next": paginated.data["next"],
                "previous": paginated.data["previous"],
                "results": paginated.data["results"],
            },
            message="Despesas obtidas com sucesso.",
        )

    def retrieve(self, request, *args, **kwargs):
        return success_response(
            data=DespesaSerializer(self.get_object()).data,
            message="Despesa obtida com sucesso.",
        )

    def create(self, request, *args, **kwargs):
        serializer = DespesaCreateSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        despesa = serializer.save()
        return success_response(
            data=DespesaSerializer(despesa).data,
            message="Despesa criada com sucesso.",
            status=status.HTTP_201_CREATED,
        )

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = DespesaSerializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(data=serializer.data, message="Despesa actualizada com sucesso.")

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        try:
            despesa = FinanceService.aprovar_despesa(int(pk), request.user, request=request)
        except Despesa.DoesNotExist:
            return error_response("Despesa não encontrada.", status=status.HTTP_404_NOT_FOUND)
        except ValueError as exc:
            return error_response(str(exc), status=status.HTTP_400_BAD_REQUEST)
        return success_response(data=DespesaSerializer(despesa).data, message="Despesa aprovada.")

    @action(detail=True, methods=["post"])
    def pay(self, request, pk=None):
        try:
            despesa = FinanceService.pagar_despesa(int(pk), request.user, request=request)
        except Despesa.DoesNotExist:
            return error_response("Despesa não encontrada.", status=status.HTTP_404_NOT_FOUND)
        except ValueError as exc:
            return error_response(str(exc), status=status.HTTP_400_BAD_REQUEST)
        return success_response(data=DespesaSerializer(despesa).data, message="Despesa paga.")

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        from apps.finance.constants import DespesaEstado

        try:
            despesa = Despesa.objects.get(pk=int(pk))
            if despesa.estado == DespesaEstado.PAGA:
                return error_response("Não é possível cancelar despesa paga.", status=status.HTTP_400_BAD_REQUEST)
            despesa.estado = DespesaEstado.CANCELADA
            despesa.save(update_fields=["estado", "updated_at"])
        except Despesa.DoesNotExist:
            return error_response("Despesa não encontrada.", status=status.HTTP_404_NOT_FOUND)
        return success_response(data=DespesaSerializer(despesa).data, message="Despesa cancelada.")


@extend_schema_view(
    list=extend_schema(tags=["Financeiro — Categorias"]),
    retrieve=extend_schema(tags=["Financeiro — Categorias"]),
    create=extend_schema(tags=["Financeiro — Categorias"]),
    partial_update=extend_schema(tags=["Financeiro — Categorias"]),
    destroy=extend_schema(tags=["Financeiro — Categorias"]),
)
class CategoriaViewSet(CategoryPermissionMixin, viewsets.ModelViewSet):
    queryset = CategoriaFinanceira.objects.all()
    serializer_class = CategoriaFinanceiraSerializer
    pagination_class = StandardPagination
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = CategoriaFinanceiraSerializer(page, many=True)
        paginated = self.get_paginated_response(serializer.data)
        return success_response(
            data={
                "count": paginated.data["count"],
                "next": paginated.data["next"],
                "previous": paginated.data["previous"],
                "results": paginated.data["results"],
            },
            message="Categorias obtidas com sucesso.",
        )


class DailyReportView(APIView):
    permission_classes = [HasModulePermission]
    required_permission = "finance.report"

    @extend_schema(tags=["Financeiro — Relatórios"])
    def get(self, request):
        return success_response(
            data=FinanceService.gerar_relatorio("daily", request=request),
            message="Relatório diário gerado.",
        )


class MonthlyReportView(APIView):
    permission_classes = [HasModulePermission]
    required_permission = "finance.report"

    @extend_schema(tags=["Financeiro — Relatórios"])
    def get(self, request):
        return success_response(
            data=FinanceService.gerar_relatorio("monthly", request=request),
            message="Relatório mensal gerado.",
        )


class YearlyReportView(APIView):
    permission_classes = [HasModulePermission]
    required_permission = "finance.report"

    @extend_schema(tags=["Financeiro — Relatórios"])
    def get(self, request):
        return success_response(
            data=FinanceService.gerar_relatorio("yearly", request=request),
            message="Relatório anual gerado.",
        )
