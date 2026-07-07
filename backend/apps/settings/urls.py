"""URLs do módulo de configurações."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.settings.views import (
    BackupViewSet,
    BillingSettingsView,
    ClinicSettingsView,
    ConsultorioViewSet,
    DepartamentoViewSet,
    EmailSettingsView,
    EmailTestView,
    EspecialidadeViewSet,
    FeatureFlagsView,
    FeriadoViewSet,
    FileSettingsView,
    HorarioViewSet,
    MonitoringView,
    SecuritySettingsView,
    SmsSettingsView,
    TipoConsultaViewSet,
    TipoExameViewSet,
)

app_name = "settings"

router = DefaultRouter()
router.register("specialties", EspecialidadeViewSet, basename="specialty")
router.register("departments", DepartamentoViewSet, basename="department")
router.register("rooms", ConsultorioViewSet, basename="room")
router.register("working-hours", HorarioViewSet, basename="working-hours")
router.register("holidays", FeriadoViewSet, basename="holiday")
router.register("consultation-types", TipoConsultaViewSet, basename="consultation-type")
router.register("laboratory/exam-types", TipoExameViewSet, basename="lab-exam-type")
router.register("backups", BackupViewSet, basename="backup")

urlpatterns = [
    path("clinic/", ClinicSettingsView.as_view(), name="clinic"),
    path("billing/", BillingSettingsView.as_view(), name="billing"),
    path("email/", EmailSettingsView.as_view(), name="email"),
    path("email/test/", EmailTestView.as_view(), name="email-test"),
    path("security/", SecuritySettingsView.as_view(), name="security"),
    path("sms/", SmsSettingsView.as_view(), name="sms"),
    path("files/", FileSettingsView.as_view(), name="files"),
    path("feature-flags/", FeatureFlagsView.as_view(), name="feature-flags"),
    path("monitoring/", MonitoringView.as_view(), name="monitoring"),
    path("", include(router.urls)),
]
