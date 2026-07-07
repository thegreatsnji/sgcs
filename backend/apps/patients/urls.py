"""URLs do módulo de pacientes."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.patients.views import (
    PatientAllergyViewSet,
    PatientChronicDiseaseViewSet,
    PatientDocumentViewSet,
    PatientEmergencyContactViewSet,
    PatientHistoryViewSet,
    PatientInsuranceViewSet,
    PatientObservationViewSet,
    PatientPhotoViewSet,
    PatientViewSet,
)

app_name = "patients"

router = DefaultRouter()
router.register("", PatientViewSet, basename="patient")
router.register(
    r"(?P<patient_pk>\d+)/emergency-contacts",
    PatientEmergencyContactViewSet,
    basename="patient-emergency-contact",
)
router.register(
    r"(?P<patient_pk>\d+)/insurances",
    PatientInsuranceViewSet,
    basename="patient-insurance",
)
router.register(
    r"(?P<patient_pk>\d+)/allergies",
    PatientAllergyViewSet,
    basename="patient-allergy",
)
router.register(
    r"(?P<patient_pk>\d+)/chronic-diseases",
    PatientChronicDiseaseViewSet,
    basename="patient-chronic-disease",
)
router.register(
    r"(?P<patient_pk>\d+)/documents",
    PatientDocumentViewSet,
    basename="patient-document",
)
router.register(
    r"(?P<patient_pk>\d+)/photos",
    PatientPhotoViewSet,
    basename="patient-photo",
)
router.register(
    r"(?P<patient_pk>\d+)/history",
    PatientHistoryViewSet,
    basename="patient-history",
)
router.register(
    r"(?P<patient_pk>\d+)/observations",
    PatientObservationViewSet,
    basename="patient-observation",
)

urlpatterns = [
    path("", include(router.urls)),
]
