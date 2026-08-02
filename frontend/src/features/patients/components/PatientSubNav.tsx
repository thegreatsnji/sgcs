import { Link, NavLink, useLocation, useParams } from "react-router-dom";

import { usePermissions } from "@/hooks/usePermissions";

interface TabItem {
  label: string;
  to: string;
  end?: boolean;
  external?: boolean;
  permission?: string;
}

export function PatientSubNav() {
  const { id } = useParams();
  const location = useLocation();
  const { hasPermission } = usePermissions();

  const tabs: TabItem[] = [
    { label: "Resumo", to: `/patients/${id}`, end: true },
    { label: "Histórico", to: `/patients/${id}/clinical` },
    { label: "Consultas", to: "/appointments/list", external: true, permission: "appointments.view" },
    { label: "Laboratório", to: "/laboratory/results", external: true, permission: "laboratory.results.view" },
    { label: "Pagamentos", to: "/billing/history", external: true, permission: "billing.view" },
    { label: "Documentos", to: `/patients/${id}/documents` },
  ];

  const visibleTabs = tabs.filter((tab) => !tab.permission || hasPermission(tab.permission));

  const tabClass = (isActive: boolean) =>
    `shrink-0 rounded-xl px-4 py-2.5 text-sm font-medium transition focus-ring ${
      isActive
        ? "bg-primary-600 text-white shadow-md shadow-primary-600/20"
        : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
    }`;

  return (
    <nav
      className="flex gap-1 overflow-x-auto rounded-2xl border border-slate-200/80 bg-white p-1.5 shadow-sm"
      aria-label="Secções do paciente"
    >
      {visibleTabs.map((tab) => {
        if (tab.external) {
          const isActive = location.pathname.startsWith(tab.to);
          return (
            <Link key={tab.label} to={tab.to} className={tabClass(isActive)}>
              {tab.label}
            </Link>
          );
        }

        return (
          <NavLink key={tab.label} to={tab.to} end={tab.end} className={({ isActive }) => tabClass(isActive)}>
            {tab.label}
          </NavLink>
        );
      })}
    </nav>
  );
}
