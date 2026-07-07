import { NavLink } from "react-router-dom";

const tabs = [
  { to: "/finance", label: "Painel", end: true },
  { to: "/finance/cash", label: "Caixas" },
  { to: "/finance/movements", label: "Movimentos" },
  { to: "/finance/expenses", label: "Despesas" },
  { to: "/finance/reports", label: "Relatórios" },
];

export function FinanceSubNav() {
  return (
    <nav className="flex flex-wrap gap-1 border-b border-slate-200">
      {tabs.map((tab) => (
        <NavLink
          key={tab.to}
          to={tab.to}
          end={tab.end}
          className={({ isActive }) =>
            `px-4 py-2 text-sm font-medium ${isActive ? "border-b-2 border-primary-600 text-primary-700" : "text-slate-500"}`
          }
        >
          {tab.label}
        </NavLink>
      ))}
    </nav>
  );
}
