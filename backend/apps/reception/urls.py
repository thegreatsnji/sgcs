"""URLs do módulo de receção."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.reception.views import ReceptionViewSet

app_name = "reception"

router = DefaultRouter()
router.register("", ReceptionViewSet, basename="reception")

urlpatterns = [
    path("", include(router.urls)),
]
