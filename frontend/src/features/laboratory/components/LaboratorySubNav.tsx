import { NavLink } from "react-router-dom";

const tabs = [
  { to: "/laboratory", label: "Painel", end: true },
  { to: "/laboratory/pending", label: "Pendentes" },
  { to: "/laboratory/today", label: "Do dia" },
  { to: "/laboratory/collection", label: "Fila de colheitas" },
  { to: "/laboratory/results", label: "Resultados" },
  { to: "/laboratory/results/history", label: "Histórico" },
];

export function LaboratorySubNav() {
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
