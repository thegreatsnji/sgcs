"""URLs principais do SGCS."""

from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from apps.doctors.api_urls import (
    discharge_urlpatterns,
    evolution_urlpatterns,
    followup_urlpatterns,
    prescription_urlpatterns,
    treatment_urlpatterns,
)
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

from core.health.views import ApiRootView, HealthView, LiveView, ReadyView

_admin_path = getattr(settings, "DJANGO_ADMIN_PATH", "admin")

urlpatterns = [
    path("", ApiRootView.as_view(), name="api-root"),
    path("health/", HealthView.as_view(), name="health"),
    path("live/", LiveView.as_view(), name="live"),
    path("ready/", ReadyView.as_view(), name="ready"),
    path(f"{_admin_path}/", admin.site.urls),
    path("api/v1/auth/", include("apps.authentication.urls")),
    path("api/v1/users/", include("apps.users.urls")),
    path("api/v1/patients/", include("apps.patients.urls")),
    path("api/v1/reception/", include("apps.reception.urls")),
    path("api/v1/appointments/", include("apps.appointments.urls")),
    path("api/v1/laboratory/", include("apps.laboratory.urls")),
    path("api/v1/billing/", include("apps.billing.urls")),
    path("api/v1/finance/", include("apps.finance.urls")),
    path("api/v1/pharmacy/", include("apps.pharmacy.urls")),
    path("api/v1/stock/", include("apps.pharmacy.stock_urls")),
    path("api/v1/reports/", include("apps.reports.urls")),
    path("api/v1/settings/", include("apps.settings.urls")),
    path("api/v1/prescriptions/", include((prescription_urlpatterns, "prescriptions"))),
    path("api/v1/treatments/", include((treatment_urlpatterns, "treatments"))),
    path("api/v1/evolutions/", include((evolution_urlpatterns, "evolutions"))),
    path("api/v1/discharges/", include((discharge_urlpatterns, "discharges"))),
    path("api/v1/followups/", include((followup_urlpatterns, "followups"))),
    path("api/v1/notifications/", include("apps.notifications.urls")),
    path("api/v1/audit-logs/", include("apps.audit_logs.urls")),
    path("api/v1/dashboard/", include("apps.dashboard.urls")),
]

if settings.DEBUG or getattr(settings, "ENABLE_API_DOCS", False):
    urlpatterns += [
        path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
        path(
            "api/docs/",
            SpectacularSwaggerView.as_view(url_name="schema"),
            name="swagger-ui",
        ),
        path(
            "api/redoc/",
            SpectacularRedocView.as_view(url_name="schema"),
            name="redoc",
        ),
    ]

if settings.DEBUG:
    try:
        import debug_toolbar

        urlpatterns = [
            path("__debug__/", include(debug_toolbar.urls)),
        ] + urlpatterns
    except ImportError:
        pass

    from django.conf.urls.static import static

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
