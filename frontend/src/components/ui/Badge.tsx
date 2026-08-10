import { Badge as DesignSystemBadge } from "@/design-system/Badge";

export type { BadgeProps } from "@/design-system/Badge";

/** @deprecated Prefer import from `@/design-system`. */
export function Badge(props: import("@/design-system/Badge").BadgeProps) {
  return <DesignSystemBadge {...props} />;
}
