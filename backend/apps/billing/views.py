"""Views do módulo de faturação."""

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.views import APIView

from apps.billing.clinic_scope import EXCLUDED_SERVICE_CATEGORIES, EXCLUDED_SERVICE_CODES
from apps.billing.filters import FaturaFilter, OrcamentoFilter, PagamentoFilter, ReciboFilter, ServicoFilter
from apps.billing.models import Fatura, Orcamento, Pagamento, Recibo, ReducaoValorAutorizacao, Servico, ServicoPrecoHistorico
from apps.billing.permissions import (
    InvoicePermissionMixin,
    PaymentPermissionMixin,
    QuotePermissionMixin,
    ReceiptPermissionMixin,
    ServicePermissionMixin,
)
from apps.billing.serializers import (
    FaturaCreateSerializer,
    FaturaSerializer,
    OrcamentoCreateSerializer,
    OrcamentoSerializer,
    PagamentoCreateSerializer,
    PagamentoSerializer,
    ReciboSerializer,
    ReducaoValorAutorizacaoSerializer,
    ReducaoValorSolicitarSerializer,
    ServicoPrecoHistoricoSerializer,
    ServicoSerializer,
)
from apps.billing.services.billing_service import BillingService
from apps.billing.services.cache_service import BillingCacheService
from apps.users.permissions import HasModulePermission
from core.pagination import StandardPagination
from core.responses import error_response, success_response


@extend_schema_view(
    list=extend_schema(tags=["Faturação — Serviços"]),
    retrieve=extend_schema(tags=["Faturação — Serviços"]),
    create=extend_schema(tags=["Faturação — Serviços"]),
    partial_update=extend_schema(tags=["Faturação — Serviços"]),
    destroy=extend_schema(tags=["Faturação — Serviços"]),
)
class ServicoViewSet(ServicePermissionMixin, viewsets.ModelViewSet):
    queryset = Servico.objects.select_related("departamento", "especialidade").all()
    serializer_class = ServicoSerializer
    pagination_class = StandardPagination
    filterset_class = ServicoFilter
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action in ("list", "retrieve") and not self.request.query_params.get(
            "include_excluded"
        ):
            qs = qs.exclude(categoria__in=EXCLUDED_SERVICE_CATEGORIES).exclude(
                codigo__in=EXCLUDED_SERVICE_CODES
            )
        if self.request.query_params.get("operacional") == "1":
            qs = qs.filter(activo=True)
        return qs

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def perform_create(self, serializer):
        serializer.save()
        BillingCacheService.invalidate_all()

    def perform_update(self, serializer):
        serializer.save()
        BillingCacheService.invalidate_all()

    def perform_destroy(self, instance):
        instance.activo = False
        instance.save(update_fields=["activo", "updated_at"])
        BillingCacheService.invalidate_all()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = ServicoSerializer(page, many=True, context={"request": request})
        paginated = self.get_paginated_response(serializer.data)
        return success_response(
            data={
                "count": paginated.data["count"],
                "next": paginated.data["next"],
                "previous": paginated.data["previous"],
                "results": paginated.data["results"],
            },
            message="Serviços obtidos com sucesso.",
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        return success_response(
            data=ServicoSerializer(instance).data,
            message="Serviço obtido com sucesso.",
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return success_response(
            data=serializer.data,
            message="Serviço criado com sucesso.",
            status=status.HTTP_201_CREATED,
        )

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return success_response(data=serializer.data, message="Serviço actualizado com sucesso.")

    @extend_schema(tags=["Faturação — Serviços"])
    @action(detail=True, methods=["get"], url_path="price-history")
    def price_history(self, request, pk=None):
        servico = self.get_object()
        historico = servico.historico_precos.select_related("alterado_por").all()[:100]
        data = ServicoPrecoHistoricoSerializer(historico, many=True).data
        return success_response(data=data, message="Histórico de preços obtido com sucesso.")


@extend_schema_view(
    list=extend_schema(tags=["Faturação — Orçamentos"]),
    retrieve=extend_schema(tags=["Faturação — Orçamentos"]),
    create=extend_schema(tags=["Faturação — Orçamentos"]),
    partial_update=extend_schema(tags=["Faturação — Orçamentos"]),
)
class OrcamentoViewSet(QuotePermissionMixin, viewsets.ModelViewSet):
    queryset = Orcamento.objects.select_related("paciente", "criado_por").prefetch_related("itens__servico")
    serializer_class = OrcamentoSerializer
    pagination_class = StandardPagination
    filterset_class = OrcamentoFilter
    http_method_names = ["get", "post", "patch", "head", "options"]

    def get_serializer_class(self):
        if self.action == "create":
            return OrcamentoCreateSerializer
        return OrcamentoSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = OrcamentoSerializer(page, many=True)
        paginated = self.get_paginated_response(serializer.data)
        return success_response(
            data={
                "count": paginated.data["count"],
                "next": paginated.data["next"],
                "previous": paginated.data["previous"],
                "results": paginated.data["results"],
            },
            message="Orçamentos obtidos com sucesso.",
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        return success_response(
            data=OrcamentoSerializer(instance).data,
            message="Orçamento obtido com sucesso.",
        )

    def create(self, request, *args, **kwargs):
        serializer = OrcamentoCreateSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        orcamento = serializer.save()
        return success_response(
            data=OrcamentoSerializer(orcamento).data,
            message="Orçamento criado com sucesso.",
            status=status.HTTP_201_CREATED,
        )

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance.is_editavel:
            return error_response("Orçamento não editável.", status=status.HTTP_400_BAD_REQUEST)
        desconto = request.data.get("desconto")
        validade = request.data.get("validade")
        update_fields = ["updated_at"]
        if desconto is not None:
            instance.desconto = desconto
            update_fields.append("desconto")
        if validade is not None:
            instance.validade = validade or None
            update_fields.append("validade")
        instance.save(update_fields=update_fields)
        BillingService._recalcular_orcamento(instance)
        instance.refresh_from_db()
        BillingCacheService.invalidate_all(patient_id=instance.paciente_id)
        return success_response(
            data=OrcamentoSerializer(instance).data,
            message="Orçamento actualizado com sucesso.",
        )

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        try:
            orcamento = BillingService.aprovar_orcamento(int(pk), request.user, request=request)
        except Orcamento.DoesNotExist:
            return error_response("Orçamento não encontrado.", status=status.HTTP_404_NOT_FOUND)
        except ValueError as exc:
            return error_response(str(exc), status=status.HTTP_400_BAD_REQUEST)
        return success_response(
            data=OrcamentoSerializer(orcamento).data,
            message="Orçamento aprovado com sucesso.",
        )

    @action(detail=True, methods=["post"], url_path="items")
    def add_item(self, request, pk=None):
        try:
            BillingService.adicionar_item_orcamento(
                int(pk),
                request.user,
                {
                    "servico_id": request.data.get("servico"),
                    "quantidade": request.data.get("quantidade", 1),
                    "preco_unitario": request.data.get("preco_unitario"),
                },
                request=request,
            )
            orcamento = Orcamento.objects.get(pk=pk)
        except Orcamento.DoesNotExist:
            return error_response("Orçamento não encontrado.", status=status.HTTP_404_NOT_FOUND)
        except ValueError as exc:
            return error_response(str(exc), status=status.HTTP_400_BAD_REQUEST)
        return success_response(
            data=OrcamentoSerializer(orcamento).data,
            message="Item adicionado com sucesso.",
            status=status.HTTP_201_CREATED,
        )


@extend_schema_view(
    list=extend_schema(tags=["Faturação — Faturas"]),
    retrieve=extend_schema(tags=["Faturação — Faturas"]),
    create=extend_schema(tags=["Faturação — Faturas"]),
    partial_update=extend_schema(tags=["Faturação — Faturas"]),
)
class FaturaViewSet(InvoicePermissionMixin, viewsets.ModelViewSet):
    queryset = Fatura.objects.select_related(
        "paciente", "consulta", "orcamento", "emitida_por"
    ).prefetch_related("itens__servico", "pagamentos")
    serializer_class = FaturaSerializer
    pagination_class = StandardPagination
    filterset_class = FaturaFilter
    http_method_names = ["get", "post", "patch", "head", "options"]

    def get_serializer_class(self):
        if self.action == "create":
            return FaturaCreateSerializer
        return FaturaSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = FaturaSerializer(page, many=True)
        paginated = self.get_paginated_response(serializer.data)
        return success_response(
            data={
                "count": paginated.data["count"],
                "next": paginated.data["next"],
                "previous": paginated.data["previous"],
                "results": paginated.data["results"],
            },
            message="Faturas obtidas com sucesso.",
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        return success_response(
            data=FaturaSerializer(instance).data,
            message="Fatura obtida com sucesso.",
        )

    def create(self, request, *args, **kwargs):
        serializer = FaturaCreateSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        fatura = serializer.save()
        return success_response(
            data=FaturaSerializer(fatura).data,
            message="Fatura criada com sucesso.",
            status=status.HTTP_201_CREATED,
        )

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance.is_editavel:
            return error_response("Fatura não editável.", status=status.HTTP_400_BAD_REQUEST)
        desconto = request.data.get("desconto")
        if desconto is not None:
            instance.desconto = desconto
            instance.save(update_fields=["desconto", "updated_at"])
            BillingService._recalcular_fatura(instance)
            instance.refresh_from_db()
        BillingCacheService.invalidate_all(patient_id=instance.paciente_id)
        return success_response(
            data=FaturaSerializer(instance).data,
            message="Fatura actualizada com sucesso.",
        )

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        try:
            fatura = BillingService.cancelar_fatura(int(pk), request.user, request=request)
        except Fatura.DoesNotExist:
            return error_response("Fatura não encontrada.", status=status.HTTP_404_NOT_FOUND)
        except ValueError as exc:
            return error_response(str(exc), status=status.HTTP_400_BAD_REQUEST)
        return success_response(
            data=FaturaSerializer(fatura).data,
            message="Fatura cancelada com sucesso.",
        )

    @action(detail=True, methods=["post"], url_path="items")
    def add_item(self, request, pk=None):
        try:
            BillingService.adicionar_item_fatura(
                int(pk),
                request.user,
                {
                    "servico_id": request.data.get("servico"),
                    "quantidade": request.data.get("quantidade", 1),
                    "preco": request.data.get("preco"),
                },
                request=request,
            )
            fatura = Fatura.objects.get(pk=pk)
        except Fatura.DoesNotExist:
            return error_response("Fatura não encontrada.", status=status.HTTP_404_NOT_FOUND)
        except ValueError as exc:
            return error_response(str(exc), status=status.HTTP_400_BAD_REQUEST)
        return success_response(
            data=FaturaSerializer(fatura).data,
            message="Item adicionado com sucesso.",
            status=status.HTTP_201_CREATED,
        )


@extend_schema_view(
    list=extend_schema(tags=["Faturação — Pagamentos"]),
    retrieve=extend_schema(tags=["Faturação — Pagamentos"]),
    create=extend_schema(tags=["Faturação — Pagamentos"]),
    partial_update=extend_schema(tags=["Faturação — Pagamentos"]),
)
class PagamentoViewSet(PaymentPermissionMixin, viewsets.ModelViewSet):
    queryset = Pagamento.objects.select_related("fatura", "recebido_por")
    serializer_class = PagamentoSerializer
    pagination_class = StandardPagination
    filterset_class = PagamentoFilter
    http_method_names = ["get", "post", "patch", "head", "options"]

    def get_serializer_class(self):
        if self.action == "create":
            return PagamentoCreateSerializer
        return PagamentoSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = PagamentoSerializer(page, many=True)
        paginated = self.get_paginated_response(serializer.data)
        return success_response(
            data={
                "count": paginated.data["count"],
                "next": paginated.data["next"],
                "previous": paginated.data["previous"],
                "results": paginated.data["results"],
            },
            message="Pagamentos obtidos com sucesso.",
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        return success_response(
            data=PagamentoSerializer(instance).data,
            message="Pagamento obtido com sucesso.",
        )

    def create(self, request, *args, **kwargs):
        serializer = PagamentoCreateSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        pagamento = serializer.save()
        return success_response(
            data=PagamentoSerializer(pagamento).data,
            message="Pagamento registado com sucesso.",
            status=status.HTTP_201_CREATED,
        )

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        referencia = request.data.get("referencia")
        metodo = request.data.get("metodo_pagamento")
        update_fields = ["updated_at"]
        if referencia is not None:
            instance.referencia = referencia
            update_fields.append("referencia")
        if metodo is not None:
            instance.metodo_pagamento = metodo
            update_fields.append("metodo_pagamento")
        instance.save(update_fields=update_fields)
        return success_response(
            data=PagamentoSerializer(instance).data,
            message="Pagamento actualizado com sucesso.",
        )

    @action(detail=True, methods=["post"])
    def confirm(self, request, pk=None):
        try:
            pagamento = BillingService.confirmar_pagamento(int(pk), request.user, request=request)
        except Pagamento.DoesNotExist:
            return error_response("Pagamento não encontrado.", status=status.HTTP_404_NOT_FOUND)
        except ValueError as exc:
            return error_response(str(exc), status=status.HTTP_400_BAD_REQUEST)
        return success_response(
            data=PagamentoSerializer(pagamento).data,
            message="Pagamento confirmado com sucesso.",
        )


@extend_schema_view(
    list=extend_schema(tags=["Faturação — Recibos"]),
    retrieve=extend_schema(tags=["Faturação — Recibos"]),
)
class ReciboViewSet(ReceiptPermissionMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Recibo.objects.select_related(
        "pagamento", "pagamento__fatura", "pagamento__fatura__paciente"
    )
    serializer_class = ReciboSerializer
    pagination_class = StandardPagination
    filterset_class = ReciboFilter

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = ReciboSerializer(page, many=True)
        paginated = self.get_paginated_response(serializer.data)
        return success_response(
            data={
                "count": paginated.data["count"],
                "next": paginated.data["next"],
                "previous": paginated.data["previous"],
                "results": paginated.data["results"],
            },
            message="Recibos obtidos com sucesso.",
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        return success_response(
            data=ReciboSerializer(instance).data,
            message="Recibo obtido com sucesso.",
        )

    @action(detail=True, methods=["get"], url_path="impressao")
    def impressao(self, request, pk=None):
        from apps.billing.services.receipt_print_service import build_receipt_print_context

        recibo = self.get_object()
        segunda = request.query_params.get("segunda_via") in ("1", "true", "sim")
        if segunda:
            recibo.segunda_via = True
            recibo.save(update_fields=["segunda_via", "updated_at"])
        return success_response(
            data=build_receipt_print_context(recibo),
            message="Dados de impressão do recibo.",
        )


class PatientFinancialHistoryView(APIView):
    permission_classes = [HasModulePermission]
    required_permission = "billing.view"

    @extend_schema(tags=["Faturação — Histórico"])
    def get(self, request, patient_id: int):
        data = BillingService.historico_financeiro(int(patient_id))
        return success_response(data=data, message="Histórico financeiro obtido com sucesso.")


class ReducaoValorAutorizacaoViewSet(InvoicePermissionMixin, viewsets.ModelViewSet):
    queryset = ReducaoValorAutorizacao.objects.select_related(
        "servico", "paciente", "solicitado_por", "decidido_por", "fatura"
    )
    serializer_class = ReducaoValorAutorizacaoSerializer
    pagination_class = StandardPagination
    http_method_names = ["get", "post", "head", "options"]

    def get_queryset(self):
        qs = super().get_queryset()
        estado = self.request.query_params.get("estado")
        if estado:
            qs = qs.filter(estado=estado)
        return qs

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = ReducaoValorAutorizacaoSerializer(page, many=True)
        paginated = self.get_paginated_response(serializer.data)
        return success_response(
            data={
                "count": paginated.data["count"],
                "next": paginated.data["next"],
                "previous": paginated.data["previous"],
                "results": paginated.data["results"],
            },
            message="Pedidos de redução obtidos com sucesso.",
        )

    def create(self, request, *args, **kwargs):
        serializer = ReducaoValorSolicitarSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        auth = serializer.save()
        return success_response(
            data=ReducaoValorAutorizacaoSerializer(auth).data,
            message="Pedido de autorização registado.",
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["post"])
    def aprovar(self, request, pk=None):
        from apps.billing.services.reduction_service import ReductionError, decidir_autorizacao_reducao

        try:
            auth = decidir_autorizacao_reducao(
                int(pk),
                request.user,
                aprovar=True,
                observacao=request.data.get("observacao", ""),
                request=request,
            )
        except ReducaoValorAutorizacao.DoesNotExist:
            return error_response("Pedido não encontrado.", status=status.HTTP_404_NOT_FOUND)
        except ReductionError as exc:
            return error_response(str(exc), status=status.HTTP_400_BAD_REQUEST)
        return success_response(
            data=ReducaoValorAutorizacaoSerializer(auth).data,
            message="Redução aprovada.",
        )

    @action(detail=True, methods=["post"])
    def rejeitar(self, request, pk=None):
        from apps.billing.services.reduction_service import ReductionError, decidir_autorizacao_reducao

        try:
            auth = decidir_autorizacao_reducao(
                int(pk),
                request.user,
                aprovar=False,
                observacao=request.data.get("observacao", ""),
                request=request,
            )
        except ReducaoValorAutorizacao.DoesNotExist:
            return error_response("Pedido não encontrado.", status=status.HTTP_404_NOT_FOUND)
        except ReductionError as exc:
            return error_response(str(exc), status=status.HTTP_400_BAD_REQUEST)
        return success_response(
            data=ReducaoValorAutorizacaoSerializer(auth).data,
            message="Redução rejeitada.",
        )


class RelatorioReducoesView(APIView):
    permission_classes = [HasModulePermission]
    required_permission = "billing.view"

    @extend_schema(tags=["Faturação — Relatórios"])
    def get(self, request):
        from django.db.models import Avg, Count, Sum

        from apps.billing.constants import EstadoAutorizacaoReducao
        from apps.billing.models import ItemFatura

        qs = ItemFatura.objects.filter(valor_reducao__gt=0).select_related(
            "fatura", "servico", "reduzido_por"
        )
        if request.query_params.get("de"):
            qs = qs.filter(fatura__emitida_em__date__gte=request.query_params["de"])
        if request.query_params.get("ate"):
            qs = qs.filter(fatura__emitida_em__date__lte=request.query_params["ate"])
        if request.query_params.get("motivo"):
            qs = qs.filter(motivo_reducao=request.query_params["motivo"])
        if request.query_params.get("rececionista"):
            qs = qs.filter(reduzido_por_id=request.query_params["rececionista"])

        agg = qs.aggregate(
            total_linhas=Count("id"),
            oficial=Sum("subtotal_oficial"),
            cobrado=Sum("subtotal"),
            reduzido=Sum("valor_reducao"),
            media_pct=Avg("percentual_reducao"),
        )
        pendentes = ReducaoValorAutorizacao.objects.filter(
            estado=EstadoAutorizacaoReducao.PENDENTE
        ).count()
        rejeitadas = ReducaoValorAutorizacao.objects.filter(
            estado=EstadoAutorizacaoReducao.REJEITADA
        ).count()

        return success_response(
            data={
                "indicadores": {
                    "numero_reducoes": agg["total_linhas"] or 0,
                    "valor_oficial_total": str(agg["oficial"] or 0),
                    "valor_cobrado_total": str(agg["cobrado"] or 0),
                    "total_reduzido": str(agg["reduzido"] or 0),
                    "media_percentual": str(agg["media_pct"] or 0),
                    "pendentes": pendentes,
                    "rejeitadas": rejeitadas,
                },
            },
            message="Relatório de reduções obtido com sucesso.",
        )
