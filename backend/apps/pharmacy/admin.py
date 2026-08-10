from django.contrib import admin

from apps.pharmacy.models import MedicamentoUrgencia, MovimentoStockUrgencia


@admin.register(MedicamentoUrgencia)
class MedicamentoUrgenciaAdmin(admin.ModelAdmin):
    list_display = ("codigo", "nome", "quantidade_stock", "stock_minimo", "activo")
    search_fields = ("codigo", "nome")
    list_filter = ("activo",)


@admin.register(MovimentoStockUrgencia)
class MovimentoStockUrgenciaAdmin(admin.ModelAdmin):
    list_display = ("medicamento", "tipo", "quantidade", "quantidade_depois", "created_at")
    list_filter = ("tipo",)
