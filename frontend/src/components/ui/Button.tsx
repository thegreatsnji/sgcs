import { Button as DesignSystemButton } from "@/design-system/Button";

export type { ButtonProps } from "@/design-system/Button";

/** @deprecated Prefer import from `@/design-system`. */
export function Button(props: import("@/design-system/Button").ButtonProps) {
  return <DesignSystemButton {...props} />;
}
