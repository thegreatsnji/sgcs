"""Filtros do módulo de faturação."""

import django_filters
from django.db.models import Q

from apps.billing.clinic_scope import EXCLUDED_SERVICE_CATEGORIES, EXCLUDED_SERVICE_CODES
from apps.billing.constants import CATALOGO_VERSAO_ATIVA
from apps.billing.models import Fatura, Orcamento, Pagamento, Recibo, Servico


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

    class Meta:
        model = Fatura
        fields = ["paciente", "consulta", "estado"]


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
