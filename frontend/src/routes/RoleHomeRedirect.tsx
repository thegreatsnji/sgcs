import { Navigate } from "react-router-dom";

import { LoadingState } from "@/design-system";
import { useAuth } from "@/contexts/AuthContext";
import { getRoleDashboardPath } from "@/utils/roleRouting";

export function RoleHomeRedirect() {
  const { user, isLoading } = useAuth();

  if (isLoading || !user) {
    return <LoadingState message="A redirecionar..." />;
  }

  return <Navigate to={getRoleDashboardPath(user.role)} replace />;
}
