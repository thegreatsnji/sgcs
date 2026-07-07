"""Admin do módulo de laboratório."""

from django.contrib import admin

from apps.laboratory.models import (
    AnexoResultado,
    ExameLaboratorial,
    ParametroResultado,
    PedidoLaboratorial,
    ResultadoLaboratorial,
)


class ExameLaboratorialInline(admin.TabularInline):
    model = ExameLaboratorial
    extra = 0


class ParametroResultadoInline(admin.TabularInline):
    model = ParametroResultado
    extra = 0


class AnexoResultadoInline(admin.TabularInline):
    model = AnexoResultado
    extra = 0
    raw_id_fields = ("ficheiro",)


@admin.register(PedidoLaboratorial)
class PedidoLaboratorialAdmin(admin.ModelAdmin):
    list_display = (
        "numero_pedido",
        "paciente",
        "estado",
        "prioridade",
        "data_pedido",
        "data_conclusao",
    )
    list_filter = ("estado", "prioridade")
    search_fields = ("numero_pedido", "paciente__full_name", "paciente__patient_number")
    raw_id_fields = ("consulta", "paciente", "medico", "pedido_consulta", "registado_por")
    inlines = [ExameLaboratorialInline]


@admin.register(ExameLaboratorial)
class ExameLaboratorialAdmin(admin.ModelAdmin):
    list_display = ("nome_exame", "pedido", "categoria", "estado")
    list_filter = ("categoria", "estado")
    raw_id_fields = ("pedido",)


@admin.register(ResultadoLaboratorial)
class ResultadoLaboratorialAdmin(admin.ModelAdmin):
    list_display = ("pedido_laboratorial", "estado", "responsavel", "data_resultado", "data_validacao")
    list_filter = ("estado",)
    search_fields = ("pedido_laboratorial__numero_pedido",)
    raw_id_fields = ("pedido_laboratorial", "responsavel", "validado_por")
    inlines = [ParametroResultadoInline, AnexoResultadoInline]

