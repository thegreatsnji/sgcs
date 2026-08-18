from django.contrib import admin

from apps.pharmacy.models import MedicamentoUrgencia, MovimentoStockUrgencia


@admin.register(MedicamentoUrgencia)
class MedicamentoUrgenciaAdmin(admin.ModelAdmin):
    list_display = ("codigo", "nome", "categoria", "quantidade_stock", "stock_minimo", "estado", "activo")
    search_fields = ("codigo", "nome")
    list_filter = ("activo", "categoria")
    readonly_fields = ("quantidade_stock",)


@admin.register(MovimentoStockUrgencia)
class MovimentoStockUrgenciaAdmin(admin.ModelAdmin):
    list_display = ("medicamento", "tipo", "quantidade", "quantidade_depois", "operador", "created_at")
    list_filter = ("tipo",)
    readonly_fields = (
        "medicamento",
        "tipo",
        "quantidade",
        "quantidade_antes",
        "quantidade_depois",
        "motivo",
        "origem",
        "operador",
        "paciente",
        "consulta",
        "created_at",
        "updated_at",
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False
