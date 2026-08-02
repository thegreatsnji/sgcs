/** Componentes legados — importações directas por ficheiro permanecem válidas. */
export { Badge } from "./Badge";
export { Button } from "./Button";
export { Card } from "./Card";
export { Dialog } from "./Dialog";
export { Input } from "./Input";
export { Modal } from "./Modal";
export { Spinner } from "./Spinner";
export { KpiCard } from "./KpiCard";
export { Toggle } from "./Toggle";

/** Re-exportações do design-system (caminho preferido para novos ecrãs). */
export {
  Badge as DesignSystemBadge,
  Button as DesignSystemButton,
  Card as DesignSystemCard,
  Input as DesignSystemInput,
  Modal as DesignSystemModal,
  LoadingState,
  EmptyState,
  ErrorState,
  Skeleton,
  SkeletonCard,
  SkeletonTable,
  Avatar,
  Pagination,
  CurrencyDisplay,
  ToastProvider,
  useToast,
} from "@/design-system";
export type {
  BadgeProps as DesignSystemBadgeProps,
  ButtonProps as DesignSystemButtonProps,
  CardProps as DesignSystemCardProps,
  InputProps as DesignSystemInputProps,
  ModalProps as DesignSystemModalProps,
  LoadingStateProps,
  EmptyStateProps,
  ErrorStateProps,
  AvatarProps,
  PaginationProps,
  CurrencyDisplayProps,
  ToastVariant,
} from "@/design-system";
