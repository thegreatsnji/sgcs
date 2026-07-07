"""Admin do módulo de consultas."""

from django.contrib import admin

from apps.appointments.models import (
    AnotacaoClinica,
    Appointment,
    Diagnostico,
    PedidoImagiologia,
    PedidoLaboratorio,
    Seguimento,
    SinaisVitais,
)


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = (
        "appointment_number",
        "patient",
        "doctor",
        "status",
        "consultation_date",
        "scheduled_at",
    )
    list_filter = ("status", "priority", "consultation_date")
    search_fields = ("appointment_number", "patient__full_name", "patient__patient_number")
    raw_id_fields = ("patient", "doctor", "receptionist", "queue_entry", "check_in", "referral", "created_by")


@admin.register(SinaisVitais)
class SinaisVitaisAdmin(admin.ModelAdmin):
    list_display = ("consulta", "pressao_arterial", "imc", "updated_at")
    raw_id_fields = ("consulta", "registado_por")


@admin.register(AnotacaoClinica)
class AnotacaoClinicaAdmin(admin.ModelAdmin):
    list_display = ("consulta", "updated_at")
    raw_id_fields = ("consulta", "registado_por")


@admin.register(Diagnostico)
class DiagnosticoAdmin(admin.ModelAdmin):
    list_display = ("consulta", "codigo_cid10", "descricao", "tipo")
    raw_id_fields = ("consulta", "registado_por")


@admin.register(PedidoLaboratorio)
class PedidoLaboratorioAdmin(admin.ModelAdmin):
    list_display = ("consulta", "tipo_exame", "estado", "prioridade")
    list_filter = ("estado", "prioridade")
    raw_id_fields = ("consulta", "solicitado_por")


@admin.register(PedidoImagiologia)
class PedidoImagiologiaAdmin(admin.ModelAdmin):
    list_display = ("consulta", "tipo_exame", "estado", "prioridade")
    list_filter = ("estado", "prioridade")
    raw_id_fields = ("consulta", "solicitado_por")


@admin.register(Seguimento)
class SeguimentoAdmin(admin.ModelAdmin):
    list_display = ("consulta", "data_retorno", "motivo")
    raw_id_fields = ("consulta", "registado_por")
