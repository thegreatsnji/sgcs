import { PillSubNav } from "@/components/layout/PillSubNav";
import { UI_COPY } from "@/constants/uiCopy";

const tabs = [
  { to: "/billing", label: UI_COPY.nav.dashboard, end: true },
  { to: "/billing/services", label: "Serviços" },
  { to: "/billing/quotes", label: "Orçamentos" },
  { to: "/billing/invoices", label: "Faturas" },
  { to: "/billing/payments", label: "Pagamentos" },
  { to: "/billing/receipts", label: "Recibos" },
];

export function BillingSubNav() {
  return <PillSubNav tabs={tabs} ariaLabel="Navegação de faturação" />;
}
