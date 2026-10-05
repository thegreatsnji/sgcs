import type { ReactNode } from "react";
import { Navigate, Outlet, useLocation } from "react-router-dom";

import { LoadingState } from "@/design-system";
import { useAuth } from "@/contexts/AuthContext";
import { usePermissions } from "@/hooks/usePermissions";
import { getRoleDashboardPath } from "@/utils/roleRouting";

export function ProtectedRoute() {
  const { isAuthenticated, isLoading } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p className="text-slate-600">A carregar...</p>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  return <Outlet />;
}

export function PublicRoute() {
  const { isAuthenticated, isLoading, user } = useAuth();

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p className="text-slate-600">A carregar...</p>
      </div>
    );
  }

  if (isAuthenticated) {
    return <Navigate to={getRoleDashboardPath(user?.role)} replace />;
  }

  return <Outlet />;
}

interface PermissionRouteProps {
  permission: string;
  fallback?: string;
}

export function PermissionRoute({ permission, fallback }: PermissionRouteProps) {
  const { hasPermission, isLoading, isError, refetchPermissions } = usePermissions();
  const { user } = useAuth();
  const roleHome = getRoleDashboardPath(user?.role);
  const resolvedFallback =
    fallback && fallback !== "/" ? fallback : roleHome !== "/" ? roleHome : "/404";

  if (isLoading) {
    return <LoadingState message="A verificar permissões..." />;
  }

  if (isError) {
    return (
      <div className="flex min-h-[40vh] flex-col items-center justify-center gap-3 p-8 text-center">
        <p className="text-slate-700">Não foi possível carregar permissões.</p>
        <button
          type="button"
          className="rounded-lg bg-primary-600 px-4 py-2 text-sm font-medium text-white"
          onClick={() => void refetchPermissions()}
        >
          Tentar novamente
        </button>
      </div>
    );
  }

  if (!hasPermission(permission)) {
    return <Navigate to={resolvedFallback} replace />;
  }

  return <Outlet />;
}

interface PermissionGuardProps {
  permission: string;
  fallback?: string;
  children: ReactNode;
}

export function PermissionGuard({ permission, fallback = "/", children }: PermissionGuardProps) {
  const { hasPermission, isLoading } = usePermissions();

  if (isLoading) {
    return <LoadingState message="A verificar permissões..." />;
  }

  if (!hasPermission(permission)) {
    return <Navigate to={fallback} replace />;
  }

  return children;
}

export function AdminOnlyRoute() {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return <LoadingState message="A verificar acesso..." />;
  }

  if (user?.role !== "ADMINISTRADOR") {
    return <Navigate to={getRoleDashboardPath(user?.role)} replace />;
  }

  return <Outlet />;
}
