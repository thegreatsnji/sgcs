export interface SpinnerProps {
  size?: "sm" | "md" | "lg";
  label?: string;
}

const sizeClasses = {
  sm: "h-4 w-4 border-2",
  md: "h-6 w-6 border-2",
  lg: "h-10 w-10 border-4",
};

export function Spinner({ size = "md", label = "A carregar..." }: SpinnerProps) {
  return (
    <div className="flex items-center gap-2" role="status" aria-live="polite">
      <span
        className={`inline-block animate-spin rounded-full border-primary-600 border-t-transparent ${sizeClasses[size]}`}
      />
      <span className="text-sm text-slate-600">{label}</span>
    </div>
  );
}
