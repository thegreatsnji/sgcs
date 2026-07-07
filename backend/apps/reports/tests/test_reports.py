"""Testes do módulo de relatórios e BI."""

import pytest
from django.core.cache import cache
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.authentication.models import User, UserRole
from apps.audit_logs.models import AuditAction, AuditLog
from apps.patients.models import Patient
from apps.reports.constants import ReportType
from apps.reports.filters import ReportFilters, resolve_date_range
from apps.reports.services.cache_service import ReportsCacheService
from apps.reports.services.csv_service import CsvExportService
from apps.reports.services.excel_service import ExcelExportService
from apps.reports.services.pdf_service import PdfExportService
from apps.reports.services.report_service import ReportService
from apps.reports.services.statistics_service import StatisticsService


@pytest.fixture(autouse=True)
def clear_reports_cache():
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def director_user(db):
    return User.objects.create_user(
        email="director@test.com",
        password="Test1234!",
        first_name="Director",
        last_name="Teste",
        role=UserRole.DIRECTOR,
    )


@pytest.fixture
def finance_user_reports(db):
    return User.objects.create_user(
        email="finance.reports@test.com",
        password="Test1234!",
        first_name="Financeiro",
        last_name="Reports",
        role=UserRole.FINANCEIRO,
    )


@pytest.fixture
def sample_patient(db, admin_user):
    return Patient.objects.create(
        first_name="Ana",
        last_name="Silva",
        birth_date="1990-05-15",
        gender="F",
        phone="955000111",
        address_city="Bissau",
        nationality="Guineense",
        created_by=admin_user,
    )


@pytest.mark.django_db
class TestReportFilters:
    def test_resolve_periodo_mes(self):
        filters = ReportFilters(periodo="mes")
        inicio, fim = resolve_date_range(filters)
        assert inicio.day == 1
        assert fim >= inicio

    def test_resolve_periodo_personalizado(self):
        filters = ReportFilters(
            periodo="personalizado",
            data_inicio=__import__("datetime").date(2025, 1, 1),
            data_fim=__import__("datetime").date(2025, 1, 31),
        )
        inicio, fim = resolve_date_range(filters)
        assert inicio.year == 2025
        assert fim.month == 1


@pytest.mark.django_db
class TestStatisticsService:
    def test_relatorio_pacientes(self, sample_patient):
        data = StatisticsService.relatorio_pacientes(ReportFilters())
        assert data["resumo"]["total"] >= 1
        assert "demografia" in data

    def test_relatorio_consultas(self):
        data = StatisticsService.relatorio_consultas(ReportFilters())
        assert "resumo" in data
        assert "por_medico" in data

    def test_relatorio_recepcao(self):
        data = StatisticsService.relatorio_recepcao(ReportFilters())
        assert "check_ins" in data["resumo"] or "check_ins" in str(data["resumo"])

    def test_relatorio_laboratorio(self):
        data = StatisticsService.relatorio_laboratorio(ReportFilters())
        assert data["tipo"] == "laboratorio"

    def test_relatorio_faturacao(self):
        data = StatisticsService.relatorio_faturacao(ReportFilters())
        assert data["tipo"] == "faturacao"

    def test_relatorio_financeiro(self):
        data = StatisticsService.relatorio_financeiro(ReportFilters())
        assert data["tipo"] == "financeiro"

    def test_series_temporais(self):
        data = StatisticsService.series_temporais()
        assert "receitas" in data
        assert "consultas" in data
        assert "pacientes" in data


@pytest.mark.django_db
class TestExportServices:
    def test_export_pdf(self):
        content = PdfExportService.export_report("Teste", {"total": 10, "itens": [{"a": 1}]})
        assert content[:4] == b"%PDF"

    def test_export_excel(self):
        content = ExcelExportService.export_report("Teste", {"total": 10})
        assert content[:2] == b"PK"

    def test_export_csv(self):
        content = CsvExportService.export_report("Teste", {"total": 10})
        assert b"total" in content


@pytest.mark.django_db
class TestReportService:
    def test_gerar_pacientes(self, sample_patient):
        data = ReportService.gerar(ReportType.PATIENTS, ReportFilters())
        assert data["tipo"] == "pacientes"
        assert "series" in data

    def test_gerar_usa_cache(self, sample_patient):
        filters = ReportFilters()
        first = ReportService.gerar(ReportType.PATIENTS, filters)
        second = ReportService.gerar(ReportType.PATIENTS, filters)
        assert first == second


@pytest.mark.django_db
class TestReportsAPI:
    def test_patients_report_requires_auth(self, api_client):
        url = reverse("reports:patients")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_patients_report_admin(self, api_client, admin_user, sample_patient):
        api_client.force_authenticate(user=admin_user)
        response = api_client.get(reverse("reports:patients"))
        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True
        assert response.data["data"]["tipo"] == "pacientes"

    def test_appointments_report(self, api_client, admin_user):
        api_client.force_authenticate(user=admin_user)
        response = api_client.get(reverse("reports:appointments"))
        assert response.status_code == status.HTTP_200_OK

    def test_reception_report(self, api_client, admin_user):
        api_client.force_authenticate(user=admin_user)
        response = api_client.get(reverse("reports:reception"))
        assert response.status_code == status.HTTP_200_OK

    def test_laboratory_report(self, api_client, admin_user):
        api_client.force_authenticate(user=admin_user)
        response = api_client.get(reverse("reports:laboratory"))
        assert response.status_code == status.HTTP_200_OK

    def test_billing_report(self, api_client, admin_user):
        api_client.force_authenticate(user=admin_user)
        response = api_client.get(reverse("reports:billing"))
        assert response.status_code == status.HTTP_200_OK

    def test_finance_report(self, api_client, admin_user):
        api_client.force_authenticate(user=admin_user)
        response = api_client.get(reverse("reports:finance"))
        assert response.status_code == status.HTTP_200_OK

    def test_charts_endpoint(self, api_client, admin_user):
        api_client.force_authenticate(user=admin_user)
        response = api_client.get(reverse("reports:charts"))
        assert response.status_code == status.HTTP_200_OK
        assert "receitas" in response.data["data"]

    def test_statistics_endpoint(self, api_client, admin_user):
        api_client.force_authenticate(user=admin_user)
        response = api_client.get(reverse("reports:statistics"))
        assert response.status_code == status.HTTP_200_OK

    def test_export_pdf(self, api_client, admin_user, sample_patient):
        api_client.force_authenticate(user=admin_user)
        response = api_client.get(reverse("reports:patients"), {"export": "pdf"})
        assert response.status_code == status.HTTP_200_OK
        assert response["Content-Type"] == "application/pdf"

    def test_export_xlsx(self, api_client, admin_user):
        api_client.force_authenticate(user=admin_user)
        response = api_client.get(reverse("reports:patients"), {"export": "xlsx"})
        assert response.status_code == status.HTTP_200_OK
        assert "spreadsheet" in response["Content-Type"]

    def test_export_csv(self, api_client, admin_user):
        api_client.force_authenticate(user=admin_user)
        response = api_client.get(reverse("reports:patients"), {"export": "csv"})
        assert response.status_code == status.HTTP_200_OK
        assert "csv" in response["Content-Type"]

    def test_periodo_filtro(self, api_client, admin_user):
        api_client.force_authenticate(user=admin_user)
        response = api_client.get(reverse("reports:patients"), {"periodo": "hoje"})
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestExecutiveDashboard:
    def test_executive_dashboard(self, api_client, director_user):
        api_client.force_authenticate(user=director_user)
        response = api_client.get(reverse("dashboard:executive"))
        assert response.status_code == status.HTTP_200_OK
        assert "indicadores" in response.data["data"]

    def test_executive_dashboard_admin(self, api_client, admin_user):
        api_client.force_authenticate(user=admin_user)
        response = api_client.get(reverse("dashboard:executive"))
        assert response.status_code == status.HTTP_200_OK

    def test_executive_creates_audit(self, api_client, director_user):
        api_client.force_authenticate(user=director_user)
        api_client.get(reverse("dashboard:executive"))
        assert AuditLog.objects.filter(action=AuditAction.DASHBOARD_VIEWED).exists()


@pytest.mark.django_db
class TestReportsRBAC:
    def test_receptionist_denied_reports(self, api_client, receptionist_user):
        api_client.force_authenticate(user=receptionist_user)
        response = api_client.get(reverse("reports:patients"))
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_director_allowed(self, api_client, director_user):
        api_client.force_authenticate(user=director_user)
        response = api_client.get(reverse("reports:patients"))
        assert response.status_code == status.HTTP_200_OK

    def test_financeiro_allowed(self, api_client, finance_user_reports):
        api_client.force_authenticate(user=finance_user_reports)
        response = api_client.get(reverse("reports:finance"))
        assert response.status_code == status.HTTP_200_OK

    def test_director_executive(self, api_client, director_user):
        api_client.force_authenticate(user=director_user)
        response = api_client.get(reverse("dashboard:executive"))
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestReportsCache:
    def test_cache_report(self):
        ReportsCacheService.set_report("patients", "mes", "abc", {"cached": True})
        assert ReportsCacheService.get_report("patients", "mes", "abc") == {"cached": True}

    def test_cache_executive(self):
        ReportsCacheService.set_executive({"kpi": 1})
        assert ReportsCacheService.get_executive()["kpi"] == 1

    def test_invalidate_all(self):
        ReportsCacheService.set_executive({"kpi": 2})
        ReportsCacheService.invalidate_all()
        assert ReportsCacheService.get_executive() is None


@pytest.mark.django_db
class TestReportsAudit:
    def test_report_created_audit(self, api_client, admin_user, sample_patient):
        api_client.force_authenticate(user=admin_user)
        api_client.get(reverse("reports:patients"))
        assert AuditLog.objects.filter(action=AuditAction.REPORT_CREATED).exists()

    def test_report_exported_audit(self, api_client, admin_user, sample_patient):
        api_client.force_authenticate(user=admin_user)
        api_client.get(reverse("reports:patients"), {"export": "csv"})
        assert AuditLog.objects.filter(action=AuditAction.REPORT_EXPORTED).exists()


@pytest.mark.django_db
class TestReportsTasks:
    def test_celery_stubs(self):
        from apps.reports.tasks import (
            enviar_relatorio,
            gerar_csv,
            gerar_excel,
            gerar_pdf,
            recalcular_estatisticas,
        )

        assert gerar_pdf("patients", "mes")["status"] == "stub"
        assert gerar_excel("patients", "mes")["status"] == "stub"
        assert gerar_csv("patients", "mes")["status"] == "stub"
        assert enviar_relatorio("patients", "pdf")["status"] == "stub"
        assert recalcular_estatisticas()["status"] == "stub"
