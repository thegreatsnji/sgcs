import { Card as DesignSystemCard } from "@/design-system/Card";

export type { CardProps } from "@/design-system/Card";

/** @deprecated Prefer import from `@/design-system`. */
export function Card(props: import("@/design-system/Card").CardProps) {
  return <DesignSystemCard {...props} />;
}
