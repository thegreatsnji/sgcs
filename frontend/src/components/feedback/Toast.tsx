import type { ReactNode } from "react";

type ToastVariant = "success" | "error" | "warning" | "info";

export interface ToastProps {
  message: string;
  variant?: ToastVariant;
  onClose?: () => void;
  children?: ReactNode;
}

const variantClasses: Record<ToastVariant, string> = {
  success: "border-green-200 bg-green-50 text-green-800",
  error: "border-red-200 bg-red-50 text-red-800",
  warning: "border-amber-200 bg-amber-50 text-amber-800",
  info: "border-primary-200 bg-primary-50 text-primary-800",
};

export function Toast({ message, variant = "info", onClose }: ToastProps) {
  return (
    <div
      className={`flex items-center justify-between gap-4 rounded-lg border px-4 py-3 text-sm shadow-sm ${variantClasses[variant]}`}
      role="alert"
    >
      <span>{message}</span>
      {onClose && (
        <button type="button" onClick={onClose} className="font-semibold">
          ✕
        </button>
      )}
    </div>
  );
}
