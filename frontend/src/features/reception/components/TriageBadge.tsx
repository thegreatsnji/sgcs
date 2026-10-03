import { TRIAGE_COLOR_LABELS } from "@/constants/reception";
import { Badge } from "@/design-system";
import type { TriageColor } from "@/types/reception";

const variantMap: Record<TriageColor, "success" | "warning" | "danger"> = {
  GREEN: "success",
  YELLOW: "warning",
  RED: "danger",
};

export function TriageBadge({ color }: { color: TriageColor | "" | undefined }) {
  if (!color) return null;
  return <Badge variant={variantMap[color]}>{TRIAGE_COLOR_LABELS[color]}</Badge>;
}
