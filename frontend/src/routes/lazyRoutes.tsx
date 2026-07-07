import { Suspense, lazy } from "react";

import { LoadingState } from "@/design-system";

export const PatientsListPage = lazy(() =>
  import("@/features/patients/pages/PatientsListPage").then((m) => ({ default: m.PatientsListPage })),
);

export const ReportsDashboardPage = lazy(() =>
  import("@/features/reports/pages/ReportsPages").then((m) => ({ default: m.ReportsDashboardPage })),
);

export const NotificationCenterPage = lazy(() =>
  import("@/features/notifications/pages/NotificationsPages").then((m) => ({
    default: m.NotificationCenterPage,
  })),
);

export function LazyPage({ children }: { children: React.ReactNode }) {
  return <Suspense fallback={<LoadingState message="A carregar módulo..." />}>{children}</Suspense>;
}
