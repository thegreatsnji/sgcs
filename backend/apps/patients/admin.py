"""Admin do módulo de pacientes."""

from django.contrib import admin

from apps.patients.models import (
    Patient,
    PatientAllergy,
    PatientChronicDisease,
    PatientDocument,
    PatientEmergencyContact,
    PatientHistory,
    PatientInsurance,
    PatientObservation,
    PatientPhoto,
)


class PatientEmergencyContactInline(admin.TabularInline):
    model = PatientEmergencyContact
    extra = 0


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ("patient_number", "full_name", "phone", "gender", "is_active", "created_at")
    list_filter = ("is_active", "is_deleted", "gender", "document_type")
    search_fields = ("full_name", "patient_number", "document_number", "phone", "email")
    readonly_fields = ("patient_number", "full_name", "created_at", "updated_at", "deleted_at")
    inlines = [PatientEmergencyContactInline]


@admin.register(PatientEmergencyContact)
class PatientEmergencyContactAdmin(admin.ModelAdmin):
    list_display = ("name", "patient", "phone", "relationship", "is_primary", "is_active")
    list_filter = ("is_primary", "is_active", "relationship")


@admin.register(PatientInsurance)
class PatientInsuranceAdmin(admin.ModelAdmin):
    list_display = ("provider_name", "policy_number", "patient", "is_primary", "is_active")
    search_fields = ("provider_name", "policy_number")


@admin.register(PatientAllergy)
class PatientAllergyAdmin(admin.ModelAdmin):
    list_display = ("allergen", "patient", "severity", "is_active")
    list_filter = ("severity", "is_active")


@admin.register(PatientChronicDisease)
class PatientChronicDiseaseAdmin(admin.ModelAdmin):
    list_display = ("disease_name", "patient", "status", "is_active")
    list_filter = ("status", "is_active")


@admin.register(PatientDocument)
class PatientDocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "patient", "document_type", "is_active", "created_at")
    list_filter = ("document_type", "is_active")


@admin.register(PatientPhoto)
class PatientPhotoAdmin(admin.ModelAdmin):
    list_display = ("patient", "is_primary", "is_active", "created_at")


@admin.register(PatientHistory)
class PatientHistoryAdmin(admin.ModelAdmin):
    list_display = ("patient", "event_type", "title", "event_date")
    list_filter = ("event_type",)
    readonly_fields = ("patient", "event_type", "title", "description", "event_date", "metadata", "created_at")


@admin.register(PatientObservation)
class PatientObservationAdmin(admin.ModelAdmin):
    list_display = ("patient", "observation_type", "is_pinned", "is_active", "created_at")
    list_filter = ("observation_type", "is_pinned", "is_active")
