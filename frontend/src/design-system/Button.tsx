import type { ButtonHTMLAttributes, ReactNode } from "react";

export type ButtonVariant = "primary" | "secondary" | "ghost" | "danger" | "outline";
export type ButtonSize = "sm" | "md" | "lg";

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  isLoading?: boolean;
  leftIcon?: ReactNode;
  rightIcon?: ReactNode;
  children: ReactNode;
}

const variantClasses: Record<ButtonVariant, string> = {
  primary:
    "bg-primary-600 text-white shadow-md shadow-primary-600/20 hover:bg-primary-700 hover:shadow-primary-600/30",
  secondary: "bg-surface-muted text-text hover:bg-border-subtle dark:hover:bg-slate-700",
  ghost: "bg-transparent text-text hover:bg-surface-muted",
  danger: "bg-red-600 text-white shadow-md shadow-red-600/20 hover:bg-red-700",
  outline: "border border-border bg-surface text-text hover:border-primary-300 hover:bg-surface-muted",
};

const sizeClasses: Record<ButtonSize, string> = {
  sm: "rounded-xl px-3 py-1.5 text-xs",
  md: "rounded-xl px-4 py-2 text-sm",
  lg: "rounded-2xl px-5 py-2.5 text-base",
};

export function Button({
  variant = "primary",
  size = "md",
  isLoading = false,
  leftIcon,
  rightIcon,
  className = "",
  disabled,
  children,
  ...props
}: ButtonProps) {
  return (
    <button
      type="button"
      disabled={disabled || isLoading}
      className={`inline-flex items-center justify-center gap-2 font-medium transition focus-ring disabled:cursor-not-allowed disabled:opacity-60 ${variantClasses[variant]} ${sizeClasses[size]} ${className}`}
      {...props}
    >
      {leftIcon}
      {isLoading ? "A carregar..." : children}
      {rightIcon}
    </button>
  );
}
