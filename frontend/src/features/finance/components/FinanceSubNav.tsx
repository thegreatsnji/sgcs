import { PillSubNav } from "@/components/layout/PillSubNav";
import { UI_COPY } from "@/constants/uiCopy";

const tabs = [
  { to: "/finance", label: UI_COPY.nav.dashboard, end: true },
  { to: "/finance/cash", label: "Caixas" },
  { to: "/finance/movements", label: "Movimentos" },
  { to: "/finance/expenses", label: "Despesas" },
  { to: "/finance/reports", label: UI_COPY.nav.reports },
];

export function FinanceSubNav() {
  return <PillSubNav tabs={tabs} ariaLabel="Navegação financeira" />;
}
