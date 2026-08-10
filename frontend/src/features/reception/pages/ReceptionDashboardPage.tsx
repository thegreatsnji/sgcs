import { Navigate } from "react-router-dom";

/** Painel legado — rececionistas usam /dashboard/reception */
export function ReceptionDashboardPage() {
  return <Navigate to="/dashboard/reception" replace />;
}
