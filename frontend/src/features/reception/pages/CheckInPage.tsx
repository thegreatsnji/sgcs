import { Navigate } from "react-router-dom";

/** Rota legada — triagem faz parte do Atendimento rápido. */
export function CheckInPage() {
  return <Navigate to="/reception/atendimento?passo=1" replace />;
}
