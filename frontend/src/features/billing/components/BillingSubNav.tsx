import { NavLink } from "react-router-dom";

const tabs = [
  { to: "/billing", label: "Painel", end: true },
  { to: "/billing/services", label: "Serviços" },
  { to: "/billing/quotes", label: "Orçamentos" },
  { to: "/billing/invoices", label: "Faturas" },
  { to: "/billing/payments", label: "Pagamentos" },
  { to: "/billing/receipts", label: "Recibos" },
];

export function BillingSubNav() {
  return (
    <nav className="flex flex-wrap gap-1 border-b border-slate-200">
      {tabs.map((tab) => (
        <NavLink
          key={tab.to}
          to={tab.to}
          end={tab.end}
          className={({ isActive }) =>
            `px-4 py-2 text-sm font-medium transition-colors ${
              isActive
                ? "border-b-2 border-primary-600 text-primary-700"
                : "text-slate-500 hover:text-slate-800"
            }`
          }
        >
          {tab.label}
        </NavLink>
      ))}
    </nav>
  );
}
