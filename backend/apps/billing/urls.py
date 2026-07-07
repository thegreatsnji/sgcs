"""URLs do módulo de faturação."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.billing.views import (
    FaturaViewSet,
    OrcamentoViewSet,
    PagamentoViewSet,
    PatientFinancialHistoryView,
    ReciboViewSet,
    ServicoViewSet,
)

app_name = "billing"

router = DefaultRouter()
router.register("services", ServicoViewSet, basename="billing-service")
router.register("quotes", OrcamentoViewSet, basename="billing-quote")
router.register("invoices", FaturaViewSet, basename="billing-invoice")
router.register("payments", PagamentoViewSet, basename="billing-payment")
router.register("receipts", ReciboViewSet, basename="billing-receipt")

urlpatterns = [
    path(
        "patient-history/<int:patient_id>/",
        PatientFinancialHistoryView.as_view(),
        name="patient-history",
    ),
    path("", include(router.urls)),
]
