"""Admin do módulo de receção."""

from django.contrib import admin

from apps.reception.models import ReceptionCheckIn, Referral, WaitingQueue


@admin.register(ReceptionCheckIn)
class ReceptionCheckInAdmin(admin.ModelAdmin):
    list_display = ("patient", "receptionist", "check_in_time", "status", "priority")
    list_filter = ("status", "priority")
    search_fields = ("patient__full_name", "patient__patient_number")


@admin.register(WaitingQueue)
class WaitingQueueAdmin(admin.ModelAdmin):
    list_display = ("position", "patient", "status", "estimated_wait_minutes")
    list_filter = ("status",)
    ordering = ("position",)


@admin.register(Referral)
class ReferralAdmin(admin.ModelAdmin):
    list_display = ("patient", "from_department", "to_department", "created_at")
    list_filter = ("to_department",)
