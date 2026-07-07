"""Admin do módulo de faturação."""

from django.contrib import admin

from apps.billing.models import (
    Fatura,
    ItemFatura,
    ItemOrcamento,
    Orcamento,
    Pagamento,
    Recibo,
    Servico,
)


class ItemOrcamentoInline(admin.TabularInline):
    model = ItemOrcamento
    extra = 0


class ItemFaturaInline(admin.TabularInline):
    model = ItemFatura
    extra = 0


@admin.register(Servico)
class ServicoAdmin(admin.ModelAdmin):
    list_display = ("codigo", "nome", "categoria", "preco", "activo")
    list_filter = ("categoria", "activo")
    search_fields = ("codigo", "nome")


@admin.register(Orcamento)
class OrcamentoAdmin(admin.ModelAdmin):
    list_display = ("numero", "paciente", "estado", "total", "validade")
    list_filter = ("estado",)
    raw_id_fields = ("paciente", "criado_por")
    inlines = [ItemOrcamentoInline]


@admin.register(Fatura)
class FaturaAdmin(admin.ModelAdmin):
    list_display = ("numero", "paciente", "estado", "total", "emitida_em")
    list_filter = ("estado",)
    raw_id_fields = ("paciente", "consulta", "orcamento", "emitida_por")
    inlines = [ItemFaturaInline]


@admin.register(Pagamento)
class PagamentoAdmin(admin.ModelAdmin):
    list_display = ("fatura", "valor", "metodo_pagamento", "estado", "data_pagamento")
    list_filter = ("estado", "metodo_pagamento")
    raw_id_fields = ("fatura", "recebido_por")


@admin.register(Recibo)
class ReciboAdmin(admin.ModelAdmin):
    list_display = ("numero", "pagamento", "emitido_em")
    raw_id_fields = ("pagamento",)
