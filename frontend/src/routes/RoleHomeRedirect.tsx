import { Navigate } from "react-router-dom";

import { LoadingState } from "@/design-system";
import { useAuth } from "@/contexts/AuthContext";
import { getRoleDashboardPath } from "@/utils/roleRouting";

export function RoleHomeRedirect() {
  const { user, isLoading } = useAuth();

  if (isLoading || !user) {
    return <LoadingState message="A redirecionar..." />;
  }

  const target = getRoleDashboardPath(user.role);
  if (target === "/" || target === "/404") {
    return (
      <div className="flex min-h-[40vh] flex-col items-center justify-center gap-3 p-8 text-center">
        <p className="text-slate-700">
          Perfil «{user.role}» sem área inicial configurada.
        </p>
        <p className="text-sm text-slate-500">
          Termine sessão e contacte o administrador, ou limpe os dados do site no browser.
        </p>
      </div>
    );
  }

  return <Navigate to={target} replace />;
}
