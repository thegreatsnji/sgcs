import type { ReactNode } from "react";
import { Navigate, Outlet, useLocation } from "react-router-dom";

import { LoadingState } from "@/design-system";
import { useAuth } from "@/contexts/AuthContext";
import { usePermissions } from "@/hooks/usePermissions";

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
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p className="text-slate-600">A carregar...</p>
      </div>
    );
  }

  if (isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  return <Outlet />;
}

interface PermissionRouteProps {
  permission: string;
  fallback?: string;
}

export function PermissionRoute({ permission, fallback = "/" }: PermissionRouteProps) {
  const { hasPermission, isLoading } = usePermissions();

  if (isLoading) {
    return <LoadingState message="A verificar permissões..." />;
  }

  if (!hasPermission(permission)) {
    return <Navigate to={fallback} replace />;
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
