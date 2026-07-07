import { NavLink } from "react-router-dom";

const tabs = [
  { to: "/settings", label: "Painel", end: true },
  { to: "/settings/clinic", label: "Clínica" },
  { to: "/settings/departments", label: "Departamentos" },
  { to: "/settings/specialties", label: "Especialidades" },
  { to: "/settings/security", label: "Segurança" },
  { to: "/settings/feature-flags", label: "Feature Flags" },
  { to: "/settings/system", label: "Sistema" },
];

export function SettingsSubNav() {
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
