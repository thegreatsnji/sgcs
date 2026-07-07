import { Link } from "react-router-dom";

import { NotificationBell } from "@/features/notifications/components/NotificationBell";
import { useAuth } from "@/contexts/AuthContext";
import { usePermissions } from "@/hooks/usePermissions";

const roleLabels: Record<string, string> = {
  ADMINISTRADOR: "Administrador",
  RECECIONISTA: "Rececionista",
  MEDICO: "Médico",
  ENFERMEIRO: "Enfermeiro",
  LABORATORIO: "Laboratório",
  FINANCEIRO: "Financeiro",
  DIRECTOR: "Director",
};

export function AppHeader() {
  const { user, logout } = useAuth();
  const { hasPermission } = usePermissions();

  return (
    <header className="border-b border-slate-200 bg-white">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
        <div className="flex items-center gap-6">
          <div>
            <h1 className="text-lg font-semibold text-primary-700">SGCS — SauVida</h1>
            <p className="text-sm text-slate-500">Sistema de Gestão Clínica</p>
          </div>
          <nav className="hidden gap-3 md:flex">
            {hasPermission("patients.view") && (
              <Link to="/patients" className="text-sm font-medium text-slate-600 hover:text-primary-700">
                Pacientes
              </Link>
            )}
            {hasPermission("reception.view") && (
              <Link to="/reception" className="text-sm font-medium text-slate-600 hover:text-primary-700">
                Receção
              </Link>
            )}
            {hasPermission("appointments.view") && (
              <Link to="/appointments" className="text-sm font-medium text-slate-600 hover:text-primary-700">
                Consultas
              </Link>
            )}
            {hasPermission("laboratory.view") && (
              <Link to="/laboratory" className="text-sm font-medium text-slate-600 hover:text-primary-700">
                Laboratório
              </Link>
            )}
            {hasPermission("billing.view") && (
              <Link to="/billing" className="text-sm font-medium text-slate-600 hover:text-primary-700">
                Faturação
              </Link>
            )}
            {(hasPermission("finance.view") || hasPermission("finance.dashboard")) && (
              <Link to="/finance" className="text-sm font-medium text-slate-600 hover:text-primary-700">
                Financeiro
              </Link>
            )}
            {(hasPermission("reports.view") || hasPermission("reports.dashboard")) && (
              <Link to="/reports" className="text-sm font-medium text-slate-600 hover:text-primary-700">
                Relatórios
              </Link>
            )}
            {(hasPermission("doctors.prescription") || user?.role === "MEDICO") && (
              <Link to="/doctor" className="text-sm font-medium text-slate-600 hover:text-primary-700">
                Médico
              </Link>
            )}
            {(hasPermission("settings.view") || user?.role === "ADMINISTRADOR") && (
              <Link to="/settings" className="text-sm font-medium text-slate-600 hover:text-primary-700">
                Configurações
              </Link>
            )}
            {(hasPermission("notifications.view") || user?.role === "ADMINISTRADOR") && (
              <Link to="/notifications" className="text-sm font-medium text-slate-600 hover:text-primary-700">
                Notificações
              </Link>
            )}
            {user?.role === "ADMINISTRADOR" && (
              <Link to="/admin/dashboard" className="text-sm font-medium text-slate-600 hover:text-primary-700">
                Administração
              </Link>
            )}
          </nav>
        </div>
        {user && (
          <div className="flex items-center gap-4">
            <NotificationBell />
            <div className="text-right">
              <p className="text-sm font-medium text-slate-900">{user.full_name}</p>
              <p className="text-xs text-slate-500">{roleLabels[user.role] ?? user.role}</p>
            </div>
            <Link
              to="/admin/profile"
              className="rounded-lg border border-slate-300 px-3 py-1.5 text-sm font-medium text-slate-700 transition hover:bg-slate-50"
            >
              Perfil
            </Link>
            <button
              type="button"
              onClick={() => void logout()}
              className="rounded-lg border border-slate-300 px-3 py-1.5 text-sm font-medium text-slate-700 transition hover:bg-slate-50"
            >
              Terminar sessão
            </button>
          </div>
        )}
      </div>
    </header>
  );
}
