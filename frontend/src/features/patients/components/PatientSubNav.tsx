import { NavLink, useParams } from "react-router-dom";

const tabs: Array<{ to: string; label: string; end?: boolean }> = [
  { to: "", label: "Resumo", end: true },
  { to: "clinical", label: "Ficha Clínica" },
  { to: "documents", label: "Documentos" },
  { to: "history", label: "Histórico" },
];

export function PatientSubNav() {
  const { id } = useParams();

  return (
    <nav className="flex flex-wrap gap-2 rounded-xl border border-slate-200 bg-white p-2 shadow-sm">
      {tabs.map((tab) => (
        <NavLink
          key={tab.label}
          to={tab.to ? `/patients/${id}/${tab.to}` : `/patients/${id}`}
          end={tab.end}
          className={({ isActive }) =>
            `rounded-lg px-4 py-2 text-sm font-medium transition ${
              isActive ? "bg-primary-600 text-white" : "text-slate-600 hover:bg-slate-100"
            }`
          }
        >
          {tab.label}
        </NavLink>
      ))}
    </nav>
  );
}
