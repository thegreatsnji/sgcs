"""URLs do módulo de relatórios."""

from django.urls import path

from apps.reports.views import (
    AppointmentsReportView,
    BillingReportView,
    ChartsView,
    FinanceReportView,
    LaboratoryReportView,
    PatientsReportView,
    ReceptionReportView,
    StatisticsView,
)

app_name = "reports"

urlpatterns = [
    path("patients/", PatientsReportView.as_view(), name="patients"),
    path("appointments/", AppointmentsReportView.as_view(), name="appointments"),
    path("reception/", ReceptionReportView.as_view(), name="reception"),
    path("laboratory/", LaboratoryReportView.as_view(), name="laboratory"),
    path("billing/", BillingReportView.as_view(), name="billing"),
    path("finance/", FinanceReportView.as_view(), name="finance"),
    path("charts/", ChartsView.as_view(), name="charts"),
    path("statistics/", StatisticsView.as_view(), name="statistics"),
]
