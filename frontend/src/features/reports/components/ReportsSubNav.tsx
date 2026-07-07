import { NavLink } from "react-router-dom";

const tabs = [
  { to: "/reports", label: "Painel", end: true },
  { to: "/reports/patients", label: "Pacientes" },
  { to: "/reports/appointments", label: "Consultas" },
  { to: "/reports/laboratory", label: "Laboratório" },
  { to: "/reports/billing", label: "Faturação" },
  { to: "/reports/finance", label: "Financeiro" },
  { to: "/reports/executive", label: "Executivo" },
];

export function ReportsSubNav() {
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
