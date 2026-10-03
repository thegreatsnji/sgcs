from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.pharmacy.views import (
    MedicamentoUrgenciaViewSet,
    MovimentoStockUrgenciaViewSet,
    StockDashboardView,
)

router = DefaultRouter()
router.register("items", MedicamentoUrgenciaViewSet, basename="stock-item")
router.register("movements", MovimentoStockUrgenciaViewSet, basename="stock-movement")

urlpatterns = [
    path("dashboard/", StockDashboardView.as_view(), name="stock-dashboard"),
    path("", include(router.urls)),
]
