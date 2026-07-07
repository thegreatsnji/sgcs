"""URLs do dashboard."""

from django.urls import path

from .views import (
    AdminDashboardView,
    BillingDashboardView,
    ClinicalDashboardView,
    ConsultasDashboardView,
    ConsultationDashboardView,
    ExecutiveDashboardView,
    FinanceDashboardView,
    LaboratoryDashboardView,
    NotificationsDashboardView,
    ReceptionDashboardView,
    SystemDashboardView,
)

app_name = "dashboard"

urlpatterns = [
    path("admin/", AdminDashboardView.as_view(), name="admin"),
    path("clinical/", ClinicalDashboardView.as_view(), name="clinical"),
    path("reception/", ReceptionDashboardView.as_view(), name="reception"),
    path("consultations/", ConsultationDashboardView.as_view(), name="consultations"),
    path("consultas/", ConsultasDashboardView.as_view(), name="consultas"),
    path("laboratory/", LaboratoryDashboardView.as_view(), name="laboratory"),
    path("billing/", BillingDashboardView.as_view(), name="billing"),
    path("finance/", FinanceDashboardView.as_view(), name="finance"),
    path("executive/", ExecutiveDashboardView.as_view(), name="executive"),
    path("notifications/", NotificationsDashboardView.as_view(), name="notifications"),
    path("system/", SystemDashboardView.as_view(), name="system"),
]
