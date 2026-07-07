import { Badge } from "@/design-system";
import { RESULTADO_STATUS_LABELS, RESULTADO_STATUS_VARIANT } from "@/constants/laboratoryResults";
import type { ResultadoEstado } from "@/types/laboratoryResult";

interface ResultadoStatusBadgeProps {
  status: ResultadoEstado;
}

export function ResultadoStatusBadge({ status }: ResultadoStatusBadgeProps) {
  return (
    <Badge variant={RESULTADO_STATUS_VARIANT[status]}>
      {RESULTADO_STATUS_LABELS[status]}
    </Badge>
  );
}
