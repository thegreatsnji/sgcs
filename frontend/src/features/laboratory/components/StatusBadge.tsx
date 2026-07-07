import { Badge } from "@/design-system";
import { LAB_STATUS_LABELS, LAB_STATUS_VARIANT } from "@/constants/laboratory";
import type { LaboratoryOrderStatus } from "@/types/laboratory";

interface StatusBadgeProps {
  status: LaboratoryOrderStatus;
}

export function StatusBadge({ status }: StatusBadgeProps) {
  return (
    <Badge variant={LAB_STATUS_VARIANT[status]}>
      {LAB_STATUS_LABELS[status]}
    </Badge>
  );
}
