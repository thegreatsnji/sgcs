import { PillSubNav } from "@/components/layout/PillSubNav";
import { UI_COPY } from "@/constants/uiCopy";

const tabs = [
  { to: "/reports", label: UI_COPY.nav.dashboard, end: true },
  { to: "/reports/patients", label: UI_COPY.nav.patients },
  { to: "/reports/appointments", label: UI_COPY.nav.appointments },
  { to: "/reports/laboratory", label: UI_COPY.nav.laboratory },
  { to: "/reports/billing", label: UI_COPY.nav.billing },
  { to: "/reports/finance", label: UI_COPY.nav.finance },
  { to: "/reports/executive", label: "Executivo" },
];

export function ReportsSubNav() {
  return <PillSubNav tabs={tabs} ariaLabel="Navegação de relatórios" />;
}
