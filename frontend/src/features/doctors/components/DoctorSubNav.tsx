import { NavLink } from "react-router-dom";

const tabs = [
  { to: "/doctor", label: "Painel", end: true },
  { to: "/doctor/prescriptions", label: "Prescrições" },
  { to: "/doctor/treatments", label: "Tratamentos" },
  { to: "/doctor/evolution", label: "Evolução" },
  { to: "/doctor/history", label: "Histórico" },
  { to: "/doctor/discharge", label: "Alta médica" },
];

export function DoctorSubNav() {
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
