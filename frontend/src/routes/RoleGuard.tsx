import type { ReactNode } from "react";
import { Navigate } from "react-router-dom";

import { LoadingState } from "@/design-system";
import { useAuth } from "@/contexts/AuthContext";
import type { UserRole } from "@/types/user";
import { getRoleDashboardPath } from "@/utils/roleRouting";

export function RoleGuard({ allowed, children }: { allowed: UserRole; children: ReactNode }) {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return <LoadingState message="A verificar acesso..." />;
  }

  if (user?.role !== allowed) {
    return <Navigate to={getRoleDashboardPath(user?.role)} replace />;
  }

  return children;
}
