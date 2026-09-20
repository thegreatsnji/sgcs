"""Filtros do módulo de faturação."""

import django_filters
from django.db.models import DecimalField, F, Q, Sum, Value
from django.db.models.functions import Coalesce

from apps.billing.clinic_scope import EXCLUDED_SERVICE_CATEGORIES, EXCLUDED_SERVICE_CODES
from apps.billing.constants import CATALOGO_VERSAO_ATIVA, FaturaEstado, PagamentoEstado
from apps.billing.models import Fatura, Orcamento, Pagamento, Recibo, Servico
from apps.billing.period import datetime_bounds, parse_iso_date, resolve_periodo


class ServicoFilter(django_filters.FilterSet):
    categoria = django_filters.CharFilter()
    activo = django_filters.BooleanFilter()
    departamento = django_filters.NumberFilter(field_name="departamento_id")
    especialidade = django_filters.NumberFilter(field_name="especialidade_id")
    operacional = django_filters.CharFilter(method="filter_operacional")
    preco_confirmado = django_filters.BooleanFilter()
    sem_preco_confirmado = django_filters.BooleanFilter(method="filter_sem_preco_confirmado")
    pendente_validacao = django_filters.BooleanFilter(method="filter_pendente_validacao")
    estado_validacao = django_filters.CharFilter(method="filter_estado_validacao")
    ordering = django_filters.OrderingFilter(
        fields=(
            ("nome", "nome"),
            ("codigo", "codigo"),
            ("preco", "preco"),
            ("ordem", "ordem"),
            ("departamento__nome", "departamento"),
        )
    )

    class Meta:
        model = Servico
        fields = ["categoria", "activo"]

    def filter_operacional(self, queryset, name, value):
        if str(value).lower() not in ("1", "true", "sim", "yes"):
            return queryset
        return (
            queryset.filter(activo=True, arquivado=False, versao_catalogo=CATALOGO_VERSAO_ATIVA)
            .exclude(categoria__in=EXCLUDED_SERVICE_CATEGORIES)
            .exclude(codigo__in=EXCLUDED_SERVICE_CODES)
            .filter(preco_confirmado=True)
        )

    def filter_sem_preco_confirmado(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(preco_confirmado=False)

    def filter_pendente_validacao(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(preco_confirmado=False, permite_faturacao_sem_preco_confirmado=False)

    def filter_estado_validacao(self, queryset, name, value):
        v = (value or "").upper()
        if v == "CONFIRMADO":
            return queryset.filter(preco_confirmado=True)
        if v == "PENDENTE":
            return queryset.filter(preco_confirmado=False, permite_faturacao_sem_preco_confirmado=False)
        if v in ("NECESSITA_REVISAO", "NECESSITA REVISÃO"):
            return queryset.filter(preco_confirmado=False, permite_faturacao_sem_preco_confirmado=True)
        return queryset

    def filter_search(self, queryset, name, value):
        return queryset.filter(Q(nome__icontains=value) | Q(codigo__icontains=value))


class OrcamentoFilter(django_filters.FilterSet):
    paciente = django_filters.NumberFilter(field_name="paciente_id")
    estado = django_filters.CharFilter()

    class Meta:
        model = Orcamento
        fields = ["paciente", "estado"]


class FaturaFilter(django_filters.FilterSet):
    paciente = django_filters.NumberFilter(field_name="paciente_id")
    consulta = django_filters.NumberFilter(field_name="consulta_id")
    estado = django_filters.CharFilter()
    search = django_filters.CharFilter(method="filter_search")
    periodo = django_filters.CharFilter(method="filter_periodo")
    data_inicio = django_filters.CharFilter(method="filter_noop")
    data_fim = django_filters.CharFilter(method="filter_noop")
    com_saldo = django_filters.BooleanFilter(method="filter_com_saldo")

    class Meta:
        model = Fatura
        fields = ["paciente", "consulta", "estado"]

    def filter_noop(self, queryset, name, value):
        # Consumido por filter_periodo via data.query_params.
        return queryset

    def filter_search(self, queryset, name, value):
        term = (value or "").strip()
        if not term:
            return queryset
        return queryset.filter(
            Q(numero__icontains=term)
            | Q(paciente__full_name__icontains=term)
            | Q(paciente__patient_number__icontains=term)
        )

    def filter_periodo(self, queryset, name, value):
        periodo = (value or "").strip().lower()
        if not periodo:
            return queryset
        params = getattr(self.request, "query_params", {}) if self.request else {}
        try:
            inicio = parse_iso_date(params.get("data_inicio"))
            fim = parse_iso_date(params.get("data_fim"))
            start_date, end_date = resolve_periodo(periodo, data_inicio=inicio, data_fim=fim)
            start_dt, end_dt = datetime_bounds(start_date, end_date)
        except ValueError:
            return queryset.none()
        return queryset.filter(emitida_em__gte=start_dt, emitida_em__lte=end_dt)

    def filter_com_saldo(self, queryset, name, value):
        if not value:
            return queryset
        annotated = queryset.exclude(estado=FaturaEstado.CANCELADA).annotate(
            pago_confirmado=Coalesce(
                Sum(
                    "pagamentos__valor",
                    filter=Q(pagamentos__estado=PagamentoEstado.CONFIRMADO),
                ),
                Value(0, output_field=DecimalField(max_digits=12, decimal_places=2)),
            )
        )
        return annotated.filter(total__gt=F("pago_confirmado")).filter(
            estado__in=[FaturaEstado.PENDENTE, FaturaEstado.PARCIAL]
        ).order_by("-created_at")


class PagamentoFilter(django_filters.FilterSet):
    fatura = django_filters.NumberFilter(field_name="fatura_id")
    estado = django_filters.CharFilter()

    class Meta:
        model = Pagamento
        fields = ["fatura", "estado"]


class ReciboFilter(django_filters.FilterSet):
    class Meta:
        model = Recibo
        fields = []
