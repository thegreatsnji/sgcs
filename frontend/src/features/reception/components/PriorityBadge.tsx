import type { QueuePriority } from "@/types/reception";

import { Badge } from "@/design-system";

const priorityVariant: Record<QueuePriority, "default" | "warning" | "danger" | "success"> = {
  LOW: "default",
  NORMAL: "default",
  HIGH: "warning",
  EMERGENCY: "danger",
};

const priorityLabels: Record<QueuePriority, string> = {
  LOW: "Baixa",
  NORMAL: "Normal",
  HIGH: "Alta",
  EMERGENCY: "Emergência",
};

export function PriorityBadge({ priority }: { priority: QueuePriority }) {
  return <Badge variant={priorityVariant[priority]}>{priorityLabels[priority]}</Badge>;
}
