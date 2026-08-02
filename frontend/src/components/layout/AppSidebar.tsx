import { memo, useMemo } from "react";
import { NavLink } from "react-router-dom";

import {
  IconBilling,
  IconCalendar,
  IconChevronLeft,
  IconDashboard,
  IconLab,
  IconLogo,
  IconLogout,
  IconPatients,
  IconSettings,
} from "@/components/icons";
import { buildSidebarConfig } from "@/constants/navigation";
import { useAuth } from "@/contexts/AuthContext";
import { usePermissions } from "@/hooks/usePermissions";

interface AppSidebarProps {
  collapsed: boolean;
  onToggle: () => void;
}

function AppSidebarComponent({ collapsed, onToggle }: AppSidebarProps) {
  const { user, logout } = useAuth();
  const { hasPermission } = usePermissions();

  const icons = useMemo(
    () => ({
      dashboard: <IconDashboard />,
      patients: <IconPatients />,
      calendar: <IconCalendar />,
      lab: <IconLab />,
      billing: <IconBilling />,
      settings: <IconSettings />,
      bell: <IconDashboard />,
    }),
    [],
  );

  const sidebar = useMemo(
    () => buildSidebarConfig(user?.role, hasPermission, icons),
    [hasPermission, icons, user?.role],
  );

  const linkClass = ({ isActive }: { isActive: boolean }) =>
    `group flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-all focus-ring ${
      isActive
        ? "bg-primary-600 text-white shadow-md shadow-primary-600/25"
        : "text-text-muted hover:bg-surface-muted hover:text-text"
    } ${collapsed ? "justify-center px-2" : ""}`;

  return (
    <aside
      className={`flex h-full flex-col border-r border-border bg-surface transition-all duration-300 ${
        collapsed ? "w-[72px]" : "w-64"
      }`}
      aria-label="Navegação principal"
    >
      <div className={`flex items-center gap-3 border-b border-border-subtle p-4 ${collapsed ? "justify-center" : ""}`}>
        <IconLogo className="h-9 w-9 shrink-0" />
        {!collapsed && (
          <div className="min-w-0">
            <p className="truncate text-base font-bold text-text">SauVida</p>
            <p className="truncate text-[10px] font-semibold tracking-widest text-primary-600 uppercase dark:text-primary-400">
              SGCS 2026
            </p>
          </div>
        )}
      </div>

      <nav className="flex-1 space-y-1 overflow-y-auto p-3">
        {sidebar.main.map((item) => (
          <NavLink key={item.to} to={item.to} end={item.end} className={linkClass} title={collapsed ? item.label : undefined}>
            <span className="shrink-0">{item.icon}</span>
            {!collapsed && <span>{item.label}</span>}
          </NavLink>
        ))}

        {sidebar.admin && !collapsed && (
          <div className="pt-4">
            <p className="px-3 pb-2 text-[10px] font-semibold tracking-widest text-text-muted uppercase">
              {sidebar.admin.label}
            </p>
            <div className="space-y-1">
              {sidebar.admin.items.map((item) => (
                <NavLink key={item.to} to={item.to} className={linkClass} title={item.label}>
                  <span className="shrink-0">{item.icon}</span>
                  <span>{item.label}</span>
                </NavLink>
              ))}
            </div>
          </div>
        )}
      </nav>

      <div className="space-y-1 border-t border-border-subtle p-3">
        {!collapsed && (
          <p className="px-3 pt-1 text-[10px] leading-relaxed font-medium tracking-wide text-text-muted uppercase">
            Fé que inspira, cuidado que transforma
          </p>
        )}

        <button
          type="button"
          onClick={() => void logout()}
          className={`flex w-full items-center gap-2 rounded-xl px-3 py-2.5 text-sm font-medium text-red-600 transition hover:bg-red-50 focus-ring dark:text-red-400 dark:hover:bg-red-950/40 ${
            collapsed ? "justify-center" : ""
          }`}
          aria-label="Terminar sessão"
          title="Terminar sessão"
        >
          <IconLogout className="h-5 w-5 shrink-0" />
          {!collapsed && <span>Terminar sessão</span>}
        </button>

        <button
          type="button"
          onClick={onToggle}
          className={`mt-1 flex w-full items-center gap-2 rounded-xl px-3 py-2 text-sm text-text-muted transition hover:bg-surface-muted focus-ring ${
            collapsed ? "justify-center" : ""
          }`}
          aria-label={collapsed ? "Expandir menu" : "Recolher menu"}
        >
          <IconChevronLeft className={`transition ${collapsed ? "rotate-180" : ""}`} />
          {!collapsed && <span>Recolher</span>}
        </button>
      </div>
    </aside>
  );
}

export const AppSidebar = memo(AppSidebarComponent);
