"""Admin do módulo financeiro."""

from django.contrib import admin

from apps.finance.models import Caixa, CategoriaFinanceira, Despesa, MovimentoFinanceiro


@admin.register(Caixa)
class CaixaAdmin(admin.ModelAdmin):
    list_display = ("codigo", "nome", "estado", "saldo_actual", "data_abertura")
    list_filter = ("estado",)


@admin.register(MovimentoFinanceiro)
class MovimentoFinanceiroAdmin(admin.ModelAdmin):
    list_display = ("caixa", "tipo", "origem", "valor", "data")
    list_filter = ("tipo", "origem")


@admin.register(Despesa)
class DespesaAdmin(admin.ModelAdmin):
    list_display = ("fornecedor", "categoria", "valor", "estado", "data")
    list_filter = ("estado", "categoria")


@admin.register(CategoriaFinanceira)
class CategoriaFinanceiraAdmin(admin.ModelAdmin):
    list_display = ("nome", "tipo", "activa")
