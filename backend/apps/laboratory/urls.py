"""URLs do módulo de laboratório."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.laboratory.result_views import LaboratoryResultViewSet
from apps.laboratory.views import LaboratoryViewSet

app_name = "laboratory"

router = DefaultRouter()
router.register("results", LaboratoryResultViewSet, basename="laboratory-result")
router.register("", LaboratoryViewSet, basename="laboratory")

urlpatterns = [
    path("", include(router.urls)),
]
