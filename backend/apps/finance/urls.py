"""URLs do módulo financeiro."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.finance.views import (
    CaixaViewSet,
    CategoriaViewSet,
    DailyReportView,
    DespesaViewSet,
    MonthlyReportView,
    MovimentoViewSet,
    YearlyReportView,
)

app_name = "finance"

router = DefaultRouter()
router.register("cash-registers", CaixaViewSet, basename="finance-cash-register")
router.register("movements", MovimentoViewSet, basename="finance-movement")
router.register("expenses", DespesaViewSet, basename="finance-expense")
router.register("categories", CategoriaViewSet, basename="finance-category")

urlpatterns = [
    path("reports/daily/", DailyReportView.as_view(), name="report-daily"),
    path("reports/monthly/", MonthlyReportView.as_view(), name="report-monthly"),
    path("reports/yearly/", YearlyReportView.as_view(), name="report-yearly"),
    path("", include(router.urls)),
]
