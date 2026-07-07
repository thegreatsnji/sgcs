import { useParams } from "react-router-dom";

import { ErrorState } from "@/design-system";
import { ConsultaClinica } from "@/features/appointments/components/ConsultaClinica";

export function ConsultationDetailPage() {
  const { id } = useParams<{ id: string }>();
  const appointmentId = Number(id);

  if (!Number.isFinite(appointmentId)) {
    return <ErrorState message="Consulta inválida." />;
  }

  return <ConsultaClinica appointmentId={appointmentId} />;
}
