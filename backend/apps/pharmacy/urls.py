"""URLs — farmácia de urgência."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.pharmacy.views import MedicamentoUrgenciaViewSet, MovimentoStockUrgenciaViewSet

app_name = "pharmacy"

router = DefaultRouter()
router.register("urgent-medicines", MedicamentoUrgenciaViewSet, basename="pharmacy-urgent-medicine")
router.register("urgent-movements", MovimentoStockUrgenciaViewSet, basename="pharmacy-urgent-movement")

urlpatterns = [
    path("", include(router.urls)),
]
