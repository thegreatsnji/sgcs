"""URLs — stock de urgência (prefixo legado /pharmacy/)."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.pharmacy.views import MedicamentoUrgenciaViewSet, MovimentoStockUrgenciaViewSet, StockDashboardView

app_name = "pharmacy"

router = DefaultRouter()
router.register("urgent-medicines", MedicamentoUrgenciaViewSet, basename="pharmacy-urgent-medicine")
router.register("urgent-movements", MovimentoStockUrgenciaViewSet, basename="pharmacy-urgent-movement")

urlpatterns = [
    path("dashboard/", StockDashboardView.as_view(), name="pharmacy-stock-dashboard"),
    path("", include(router.urls)),
]
