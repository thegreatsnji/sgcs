"""URLs do módulo Médicos — montadas em /api/v1/prescriptions/, etc."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.doctors.views import (
    AltaViewSet,
    EvolucaoViewSet,
    PrescricaoViewSet,
    SeguimentoViewSet,
    TratamentoViewSet,
)

prescription_router = DefaultRouter()
prescription_router.register("", PrescricaoViewSet, basename="prescription")

treatment_router = DefaultRouter()
treatment_router.register("", TratamentoViewSet, basename="treatment")

evolution_router = DefaultRouter()
evolution_router.register("", EvolucaoViewSet, basename="evolution")

discharge_router = DefaultRouter()
discharge_router.register("", AltaViewSet, basename="discharge")

followup_router = DefaultRouter()
followup_router.register("", SeguimentoViewSet, basename="followup")

prescription_urlpatterns = [path("", include(prescription_router.urls))]
treatment_urlpatterns = [path("", include(treatment_router.urls))]
evolution_urlpatterns = [path("", include(evolution_router.urls))]
discharge_urlpatterns = [path("", include(discharge_router.urls))]
followup_urlpatterns = [path("", include(followup_router.urls))]
