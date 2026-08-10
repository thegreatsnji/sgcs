import { createBrowserRouter, Navigate } from "react-router-dom";

import { PatientClinicalPage } from "@/features/patients/pages/PatientClinicalPage";
import { PatientDetailPage } from "@/features/patients/pages/PatientDetailPage";
import { PatientDocumentsPage } from "@/features/patients/pages/PatientDocumentsPage";
import { PatientFormPage } from "@/features/patients/pages/PatientFormPage";
import { PatientHistoryPage } from "@/features/patients/pages/PatientHistoryPage";
import { PatientsListPage } from "@/features/patients/pages/PatientsListPage";
import { CheckInPage } from "@/features/reception/pages/CheckInPage";
import { ReceptionDashboardPage } from "@/features/reception/pages/ReceptionDashboardPage";
import { ReceptionWorkflowPage } from "@/features/reception/pages/ReceptionWorkflowPage";
import { ReferralPage } from "@/features/reception/pages/ReferralPage";
import { WaitingQueuePage } from "@/features/reception/pages/WaitingQueuePage";
import { ConsultationDashboardPage } from "@/features/appointments/pages/ConsultationDashboardPage";
import { ConsultationDetailPage } from "@/features/appointments/pages/ConsultationDetailPage";
import { ConsultationHistoryPage } from "@/features/appointments/pages/ConsultationHistoryPage";
import { ConsultationQueuePage } from "@/features/appointments/pages/ConsultationQueuePage";
import { AppointmentDetailPage } from "@/features/appointments/pages/AppointmentDetailPage";
import { AppointmentEditPage } from "@/features/appointments/pages/AppointmentEditPage";
import { AppointmentFormPage } from "@/features/appointments/pages/AppointmentFormPage";
import { AppointmentsCalendarPage } from "@/features/appointments/pages/AppointmentsCalendarPage";
import { AppointmentsDashboardPage } from "@/features/appointments/pages/AppointmentsDashboardPage";
import { AppointmentsListPage } from "@/features/appointments/pages/AppointmentsListPage";
import { AppointmentsQueuePage } from "@/features/appointments/pages/AppointmentsQueuePage";
import { LaboratoryCollectionPage } from "@/features/laboratory/pages/LaboratoryCollectionPage";
import { LaboratoryDashboardPage } from "@/features/laboratory/pages/LaboratoryDashboardPage";
import { LaboratoryDetailPage } from "@/features/laboratory/pages/LaboratoryDetailPage";
import { LaboratoryPendingPage } from "@/features/laboratory/pages/LaboratoryPendingPage";
import { LaboratoryTodayPage } from "@/features/laboratory/pages/LaboratoryTodayPage";
import { ResultCreatePage } from "@/features/laboratory/results/pages/ResultCreatePage";
import { ResultDetailPage } from "@/features/laboratory/results/pages/ResultDetailPage";
import { ResultEditPage } from "@/features/laboratory/results/pages/ResultEditPage";
import { ResultHistoryPage } from "@/features/laboratory/results/pages/ResultHistoryPage";
import { ResultsDashboardPage } from "@/features/laboratory/results/pages/ResultsDashboardPage";
import { BillingDashboardPage } from "@/features/billing/pages/BillingDashboardPage";
import { InvoiceCreatePage } from "@/features/billing/pages/InvoiceCreatePage";
import { PendingReductionsPage } from "@/features/billing/pages/PendingReductionsPage";
import { UrgentStockPage } from "@/features/pharmacy/pages/UrgentStockPage";
import { InvoiceDetailPage } from "@/features/billing/pages/InvoiceDetailPage";
import { InvoicesListPage } from "@/features/billing/pages/InvoicesListPage";
import { PatientHistoryPage as BillingPatientHistoryPage } from "@/features/billing/pages/PatientHistoryPage";
import { PaymentsListPage } from "@/features/billing/pages/PaymentsListPage";
import { QuoteCreatePage } from "@/features/billing/pages/QuoteCreatePage";
import { QuotesListPage } from "@/features/billing/pages/QuotesListPage";
import { ReceiptDetailPage } from "@/features/billing/pages/ReceiptDetailPage";
import { ReceiptsListPage } from "@/features/billing/pages/ReceiptsListPage";
import { ServiceDetailPage } from "@/features/billing/pages/ServiceDetailPage";
import { ServiceFormPage } from "@/features/billing/pages/ServiceFormPage";
import { ServicesListPage } from "@/features/billing/pages/ServicesListPage";
import { CashMovementsPage } from "@/features/finance/pages/CashMovementsPage";
import { CashRegisterDetailPage } from "@/features/finance/pages/CashRegisterDetailPage";
import { CashRegistersPage } from "@/features/finance/pages/CashRegistersPage";
import { ExpenseFormPage } from "@/features/finance/pages/ExpenseFormPage";
import { ExpensesPage } from "@/features/finance/pages/ExpensesPage";
import { FinanceDashboardPage } from "@/features/finance/pages/FinanceDashboardPage";
import { FinanceReportsPage } from "@/features/finance/pages/FinanceReportsPage";
import {
  AppointmentsReportPage,
  BillingReportPage,
  ExecutiveReportPage,
  FinanceReportPage,
  LaboratoryReportPage,
  PatientsReportPage,
  ReportsDashboardPage,
} from "@/features/reports/pages/ReportsPages";
import {
  BackupPage,
  BillingSettingsPage,
  ClinicSettingsPage,
  ConsultationTypesPage,
  DepartmentsPage,
  EmailSettingsPage,
  FeatureFlagsPage,
  LaboratorySettingsPage,
  RoomsPage,
  SecuritySettingsPage,
  SettingsDashboardPage,
  SpecialtiesPage,
  SystemStatusPage,
  WorkingHoursPage,
} from "@/features/settings/pages/SettingsPages";
import { MedicoProfilesPage } from "@/features/settings/pages/MedicoProfilesPage";
import {
  ClinicalEvolutionPage,
} from "@/features/doctors/pages/ClinicalEvolutionPage";
import {
  DischargePage,
  DoctorDashboardPage,
  HistoryPage,
  PrescriptionsPage,
  TreatmentsPage,
} from "@/features/doctors/pages/DoctorPages";
import {
  EmailHistoryPage,
  NotificationCenterPage,
  NotificationsDashboardPage,
  PreferencesPage,
  SMSHistoryPage,
  TemplatesPage,
} from "@/features/notifications/pages/NotificationsPages";
import { AdminLayout } from "@/layouts/AdminLayout";
import { AppLayout } from "@/layouts/AppLayout";
import { AuthLayout } from "@/layouts/AuthLayout";
import { AdminDashboardPage } from "@/pages/admin/AdminDashboardPage";
import { AuditPage } from "@/pages/admin/AuditPage";
import { GroupsPage } from "@/pages/admin/GroupsPage";
import { PermissionsPage } from "@/pages/admin/PermissionsPage";
import { ProfilePage } from "@/pages/admin/ProfilePage";
import { UserFormPage } from "@/pages/admin/UserFormPage";
import { UsersListPage } from "@/pages/admin/UsersListPage";
import { LoginPage } from "@/pages/LoginPage";
import { NotFoundPage } from "@/pages/NotFoundPage";
import { AdminRoleDashboardPage } from "@/pages/dashboards/AdminRoleDashboardPage";
import { DirectorRoleDashboardPage } from "@/pages/dashboards/DirectorRoleDashboardPage";
import { DoctorRoleDashboardPage } from "@/pages/dashboards/DoctorRoleDashboardPage";
import { LaboratoryRoleDashboardPage } from "@/pages/dashboards/LaboratoryRoleDashboardPage";
import { NurseTriagePage } from "@/features/nursing/pages/NurseTriagePage";
import { NurseRoleDashboardPage } from "@/pages/dashboards/NurseRoleDashboardPage";
import { ReceptionRoleDashboardPage } from "@/pages/dashboards/ReceptionRoleDashboardPage";
import { ProtectedRoute, PublicRoute, PermissionRoute, PermissionGuard, AdminOnlyRoute } from "@/routes/guards";
import { RoleGuard } from "@/routes/RoleGuard";
import { RoleHomeRedirect } from "@/routes/RoleHomeRedirect";

export const router = createBrowserRouter([
  {
    element: <ProtectedRoute />,
    children: [
      {
        element: <AppLayout />,
        children: [
          { index: true, element: <RoleHomeRedirect /> },
          { path: "dashboard/admin", element: <RoleGuard allowed="ADMINISTRADOR"><AdminRoleDashboardPage /></RoleGuard> },
          { path: "dashboard/director", element: <RoleGuard allowed="DIRECTOR"><DirectorRoleDashboardPage /></RoleGuard> },
          { path: "dashboard/doctor", element: <RoleGuard allowed="MEDICO"><DoctorRoleDashboardPage /></RoleGuard> },
          { path: "dashboard/reception", element: <RoleGuard allowed="RECECIONISTA"><ReceptionRoleDashboardPage /></RoleGuard> },
          { path: "dashboard/laboratory", element: <RoleGuard allowed="LABORATORIO"><LaboratoryRoleDashboardPage /></RoleGuard> },
          { path: "dashboard/nurse", element: <RoleGuard allowed="ENFERMEIRO"><NurseRoleDashboardPage /></RoleGuard> },
          {
            element: (
              <RoleGuard allowed="ENFERMEIRO">
                <PermissionRoute permission="reception.view" fallback="/" />
              </RoleGuard>
            ),
            children: [{ path: "nursing/triage", element: <NurseTriagePage /> }],
          },
          {
            element: <PermissionRoute permission="patients.view" fallback="/" />,
            children: [
              { path: "patients", element: <PatientsListPage /> },
              { path: "patients/:id/edit", element: <PatientFormPage /> },
              { path: "patients/:id/clinical", element: <PatientClinicalPage /> },
              { path: "patients/:id/documents", element: <PatientDocumentsPage /> },
              { path: "patients/:id/history", element: <PatientHistoryPage /> },
              { path: "patients/:id", element: <PatientDetailPage /> },
            ],
          },
          {
            element: <PermissionRoute permission="reception.view" />,
            children: [
              { path: "reception", element: <ReceptionDashboardPage /> },
              { path: "reception/atendimento", element: <ReceptionWorkflowPage /> },
              { path: "reception/check-in", element: <CheckInPage /> },
              { path: "reception/queue", element: <WaitingQueuePage /> },
              { path: "reception/referrals", element: <ReferralPage /> },
            ],
          },
          {
            element: <PermissionRoute permission="appointments.view" fallback="/" />,
            children: [
              { path: "appointments", element: <AppointmentsDashboardPage /> },
              { path: "appointments/calendar", element: <AppointmentsCalendarPage /> },
              { path: "appointments/list", element: <AppointmentsListPage /> },
              { path: "appointments/queue", element: <AppointmentsQueuePage /> },
              { path: "appointments/new", element: <AppointmentFormPage /> },
              { path: "appointments/:id/edit", element: <AppointmentEditPage /> },
              { path: "appointments/:id", element: <AppointmentDetailPage /> },
              { path: "consultations", element: <ConsultationDashboardPage /> },
              { path: "consultations/queue", element: <ConsultationQueuePage /> },
              { path: "consultations/history", element: <ConsultationHistoryPage /> },
              { path: "consultations/:id", element: <ConsultationDetailPage /> },
            ],
          },
          {
            element: <PermissionRoute permission="laboratory.view" fallback="/" />,
            children: [
              { path: "laboratory", element: <LaboratoryDashboardPage /> },
              { path: "laboratory/pending", element: <LaboratoryPendingPage /> },
              { path: "laboratory/today", element: <LaboratoryTodayPage /> },
              { path: "laboratory/collection", element: <LaboratoryCollectionPage /> },
            ],
          },
          {
            element: <PermissionRoute permission="laboratory.results.view" fallback="/" />,
            children: [
              { path: "laboratory/results", element: <ResultsDashboardPage /> },
              { path: "laboratory/results/history", element: <ResultHistoryPage /> },
              { path: "laboratory/results/new", element: <ResultCreatePage /> },
              { path: "laboratory/results/:id/edit", element: <ResultEditPage /> },
              { path: "laboratory/results/:id", element: <ResultDetailPage /> },
            ],
          },
          {
            element: <PermissionRoute permission="laboratory.view" fallback="/" />,
            children: [
              { path: "laboratory/:id", element: <LaboratoryDetailPage /> },
            ],
          },
          {
            element: <PermissionRoute permission="billing.view" fallback="/" />,
            children: [
              { path: "billing", element: <BillingDashboardPage /> },
              { path: "billing/services", element: <ServicesListPage /> },
              { path: "billing/services/:id", element: <ServiceDetailPage /> },
              { path: "billing/quotes", element: <QuotesListPage /> },
              { path: "billing/invoices", element: <InvoicesListPage /> },
              { path: "billing/reducoes/pendentes", element: <PendingReductionsPage /> },
              { path: "billing/payments", element: <PaymentsListPage /> },
              { path: "billing/receipts", element: <ReceiptsListPage /> },
              { path: "billing/history", element: <BillingPatientHistoryPage /> },
              { path: "billing/receipts/:id", element: <ReceiptDetailPage /> },
              { path: "billing/invoices/:id", element: <InvoiceDetailPage /> },
            ],
          },
          {
            element: <PermissionRoute permission="billing.create" fallback="/billing" />,
            children: [
              { path: "billing/services/new", element: <ServiceFormPage /> },
              { path: "billing/services/:id/edit", element: <ServiceFormPage /> },
              { path: "billing/quotes/new", element: <QuoteCreatePage /> },
              { path: "billing/invoices/new", element: <InvoiceCreatePage /> },
            ],
          },
          {
            element: <PermissionRoute permission="finance.view" fallback="/" />,
            children: [
              { path: "finance", element: <FinanceDashboardPage /> },
              { path: "finance/cash", element: <CashRegistersPage /> },
              { path: "finance/cash/:id", element: <CashRegisterDetailPage /> },
              { path: "finance/movements", element: <CashMovementsPage /> },
              { path: "finance/expenses", element: <ExpensesPage /> },
              { path: "finance/reports", element: <FinanceReportsPage /> },
            ],
          },
          {
            element: <PermissionRoute permission="finance.create" fallback="/finance/expenses" />,
            children: [{ path: "finance/expenses/new", element: <ExpenseFormPage /> }],
          },
          {
            element: <PermissionRoute permission="pharmacy.view" fallback="/" />,
            children: [{ path: "pharmacy/urgent-stock", element: <UrgentStockPage /> }],
          },
          {
            element: <PermissionRoute permission="reports.view" fallback="/" />,
            children: [
              { path: "reports", element: <ReportsDashboardPage /> },
              { path: "reports/patients", element: <PatientsReportPage /> },
              { path: "reports/appointments", element: <AppointmentsReportPage /> },
              { path: "reports/laboratory", element: <LaboratoryReportPage /> },
              { path: "reports/billing", element: <BillingReportPage /> },
              { path: "reports/finance", element: <FinanceReportPage /> },
              { path: "reports/executive", element: <ExecutiveReportPage /> },
            ],
          },
          {
            element: <PermissionRoute permission="settings.view" fallback="/" />,
            children: [
              { path: "settings", element: <SettingsDashboardPage /> },
              { path: "settings/clinic", element: <ClinicSettingsPage /> },
              { path: "settings/departments", element: <DepartmentsPage /> },
              { path: "settings/specialties", element: <SpecialtiesPage /> },
              { path: "settings/medicos", element: <MedicoProfilesPage /> },
              { path: "settings/rooms", element: <RoomsPage /> },
              { path: "settings/hours", element: <WorkingHoursPage /> },
              { path: "settings/consultation-types", element: <ConsultationTypesPage /> },
              { path: "settings/laboratory", element: <LaboratorySettingsPage /> },
              { path: "settings/billing", element: <BillingSettingsPage /> },
              { path: "settings/email", element: <EmailSettingsPage /> },
              { path: "settings/security", element: <SecuritySettingsPage /> },
              { path: "settings/backups", element: <BackupPage /> },
              { path: "settings/system", element: <SystemStatusPage /> },
              { path: "settings/feature-flags", element: <FeatureFlagsPage /> },
            ],
          },
          {
            element: <PermissionRoute permission="doctors.prescription" fallback="/" />,
            children: [
              { path: "doctor", element: <DoctorDashboardPage /> },
              { path: "doctor/prescriptions", element: <PrescriptionsPage /> },
              { path: "doctor/treatments", element: <TreatmentsPage /> },
              { path: "doctor/evolution", element: <ClinicalEvolutionPage /> },
              { path: "doctor/history", element: <HistoryPage /> },
              { path: "doctor/discharge", element: <DischargePage /> },
            ],
          },
          {
            element: <PermissionRoute permission="notifications.view" fallback="/" />,
            children: [
              { path: "notifications", element: <NotificationCenterPage /> },
              { path: "notifications/history", element: <EmailHistoryPage /> },
              { path: "notifications/sms", element: <SMSHistoryPage /> },
              { path: "notifications/templates", element: <TemplatesPage /> },
              { path: "notifications/preferences", element: <PreferencesPage /> },
              { path: "notifications/dashboard", element: <NotificationsDashboardPage /> },
            ],
          },
          {
            path: "patients/new",
            element: (
              <PermissionGuard permission="patients.create" fallback="/patients">
                <PatientFormPage />
              </PermissionGuard>
            ),
          },
          {
            path: "admin",
            element: <AdminOnlyRoute />,
            children: [
              {
                element: <AdminLayout />,
                children: [
              { index: true, element: <Navigate to="dashboard" replace /> },
              { path: "dashboard", element: <AdminDashboardPage /> },
              { path: "users", element: <UsersListPage /> },
              { path: "users/new", element: <UserFormPage /> },
              { path: "users/:id/edit", element: <UserFormPage /> },
              { path: "permissions", element: <PermissionsPage /> },
              { path: "groups", element: <GroupsPage /> },
              { path: "audit", element: <AuditPage /> },
              { path: "profile", element: <ProfilePage /> },
                ],
              },
            ],
          },
        ],
      },
    ],
  },
  {
    element: <PublicRoute />,
    children: [
      {
        element: <AuthLayout />,
        children: [{ path: "login", element: <LoginPage /> }],
      },
    ],
  },
  { path: "/404", element: <NotFoundPage /> },
  { path: "*", element: <Navigate to="/404" replace /> },
]);
