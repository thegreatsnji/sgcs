import type { ReactNode } from "react";

import { UI_COPY } from "@/constants/uiCopy";
import type { UserRole } from "@/types/user";
import { getRoleDashboardPath } from "@/utils/roleRouting";

export interface SidebarNavItem {
  to: string;
  label: string;
  icon: ReactNode;
  end?: boolean;
}

export interface SidebarNavSection {
  label: string;
  items: SidebarNavItem[];
}

export type SidebarConfig = {
  main: SidebarNavItem[];
  admin?: SidebarNavSection;
};

type PermissionCheck = (permission: string) => boolean;

export function buildSidebarConfig(
  role: UserRole | undefined,
  hasPermission: PermissionCheck,
  icons: {
    dashboard: ReactNode;
    patients: ReactNode;
    calendar: ReactNode;
    lab: ReactNode;
    billing: ReactNode;
    settings: ReactNode;
    bell: ReactNode;
  },
): SidebarConfig {
  const dashboardPath = getRoleDashboardPath(role);

  const nav = UI_COPY.nav;

  if (role === "ADMINISTRADOR") {
    return {
      main: [
        { to: dashboardPath, label: nav.dashboard, icon: icons.dashboard, end: true },
        { to: "/patients", label: nav.patients, icon: icons.patients },
        { to: "/appointments", label: nav.appointments, icon: icons.calendar },
        { to: "/doctor", label: nav.doctors, icon: icons.calendar },
        { to: "/laboratory", label: nav.laboratory, icon: icons.lab },
        { to: "/billing", label: nav.billing, icon: icons.billing },
        { to: "/reports", label: nav.reports, icon: icons.dashboard },
        { to: "/notifications", label: nav.notifications, icon: icons.bell },
      ],
      admin: {
        label: nav.administration,
        items: [
          { to: "/admin/users", label: nav.users, icon: icons.settings },
          { to: "/admin/permissions", label: nav.roles, icon: icons.settings },
          { to: "/settings", label: nav.settings, icon: icons.settings },
          { to: "/settings/system", label: nav.monitoring, icon: icons.settings },
          { to: "/admin/audit", label: nav.audit, icon: icons.settings },
          { to: "/settings/backups", label: nav.backups, icon: icons.settings },
          { to: "/settings/feature-flags", label: nav.features, icon: icons.settings },
        ],
      },
    };
  }

  if (role === "DIRECTOR") {
    return {
      main: [
        { to: dashboardPath, label: nav.dashboard, icon: icons.dashboard, end: true },
        { to: "/patients", label: nav.patients, icon: icons.patients },
        { to: "/appointments", label: nav.appointments, icon: icons.calendar },
        { to: "/doctor", label: nav.doctors, icon: icons.calendar },
        { to: "/laboratory", label: nav.laboratory, icon: icons.lab },
        { to: "/billing", label: nav.billing, icon: icons.billing },
        ...(hasPermission("pharmacy.view")
          ? [{ to: "/pharmacy/urgent-stock", label: nav.pharmacyUrgent, icon: icons.lab }]
          : []),
        { to: "/finance", label: nav.finance, icon: icons.billing },
        { to: "/reports", label: nav.reports, icon: icons.dashboard },
        { to: "/notifications", label: nav.notifications, icon: icons.bell },
      ],
    };
  }

  if (role === "MEDICO") {
    return {
      main: [
        { to: dashboardPath, label: nav.dashboard, icon: icons.dashboard, end: true },
        { to: "/appointments", label: nav.todayAppointments, icon: icons.calendar },
        { to: "/patients", label: nav.patients, icon: icons.patients },
        { to: "/consultations", label: nav.clinicalRecords, icon: icons.calendar },
        { to: "/laboratory/results", label: nav.labResultsShort, icon: icons.lab },
        ...(hasPermission("pharmacy.view")
          ? [{ to: "/pharmacy/urgent-stock", label: nav.pharmacyUrgent, icon: icons.lab }]
          : []),
        { to: "/consultations/history", label: nav.followUps, icon: icons.calendar },
        { to: "/notifications", label: nav.notifications, icon: icons.bell },
      ],
    };
  }

  if (role === "RECECIONISTA") {
    return {
      main: [
        { to: dashboardPath, label: nav.dashboard, icon: icons.dashboard, end: true },
        { to: "/reception/atendimento?passo=1", label: nav.fastReception, icon: icons.patients },
        { to: "/reception/queue", label: nav.queue, icon: icons.patients },
        ...(hasPermission("billing.view")
          ? [{ to: "/billing/invoices", label: nav.billing, icon: icons.billing }]
          : []),
        { to: "/patients", label: nav.patients, icon: icons.patients },
        { to: "/appointments", label: nav.appointmentsSchedule, icon: icons.calendar },
        { to: "/notifications", label: nav.notifications, icon: icons.bell },
      ],
    };
  }

  if (role === "ENFERMEIRO") {
    return {
      main: [
        { to: dashboardPath, label: nav.dashboard, icon: icons.dashboard, end: true },
        ...(hasPermission("reception.view")
          ? [
              { to: "/nursing/triage", label: nav.checkIn, icon: icons.patients },
              { to: "/reception/queue", label: nav.queue, icon: icons.patients },
            ]
          : []),
        ...(hasPermission("pharmacy.view")
          ? [{ to: "/pharmacy/urgent-stock", label: nav.pharmacyUrgent, icon: icons.lab }]
          : []),
        { to: "/patients", label: nav.patients, icon: icons.patients },
        { to: "/appointments", label: nav.appointments, icon: icons.calendar },
      ],
    };
  }

  if (role === "LABORATORIO") {
    return {
      main: [
        { to: dashboardPath, label: nav.dashboard, icon: icons.dashboard, end: true },
        { to: "/laboratory/pending", label: nav.pending, icon: icons.lab },
        { to: "/laboratory/collection", label: nav.collection, icon: icons.lab },
        { to: "/laboratory/results", label: nav.results, icon: icons.lab },
        { to: "/laboratory/results/history", label: nav.history, icon: icons.lab },
        { to: "/notifications", label: nav.notifications, icon: icons.bell },
      ],
    };
  }

  return {
    main: [
      { to: dashboardPath, label: nav.dashboard, icon: icons.dashboard, end: true },
      ...(hasPermission("patients.view") ? [{ to: "/patients", label: nav.patients, icon: icons.patients }] : []),
      ...(hasPermission("appointments.view") ? [{ to: "/appointments", label: nav.appointments, icon: icons.calendar }] : []),
      ...(hasPermission("laboratory.view") ? [{ to: "/laboratory", label: nav.laboratory, icon: icons.lab }] : []),
      ...(hasPermission("billing.view") ? [{ to: "/billing", label: nav.billing, icon: icons.billing }] : []),
      ...(hasPermission("pharmacy.view")
        ? [{ to: "/pharmacy/urgent-stock", label: nav.pharmacyUrgent, icon: icons.lab }]
        : []),
      ...(hasPermission("finance.view") ? [{ to: "/finance", label: nav.finance, icon: icons.billing }] : []),
      ...(hasPermission("reports.view") ? [{ to: "/reports", label: nav.reports, icon: icons.dashboard }] : []),
      ...(hasPermission("notifications.view") ? [{ to: "/notifications", label: nav.notifications, icon: icons.bell }] : []),
    ],
  };
}
