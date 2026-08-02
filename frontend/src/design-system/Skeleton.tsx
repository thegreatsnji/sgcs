interface SkeletonProps {
  className?: string;
}

export function Skeleton({ className = "" }: SkeletonProps) {
  return (
    <div
      className={`animate-pulse rounded-lg bg-border dark:bg-slate-700/70 ${className}`}
      aria-hidden
    />
  );
}

export function SkeletonCard() {
  return (
    <div className="rounded-2xl border border-border bg-surface p-5 shadow-sm">
      <Skeleton className="h-3 w-24" />
      <Skeleton className="mt-4 h-8 w-20" />
      <Skeleton className="mt-4 h-5 w-16" />
    </div>
  );
}

export function SkeletonTable({ rows = 5 }: { rows?: number }) {
  return (
    <div className="space-y-3">
      {Array.from({ length: rows }).map((_, i) => (
        <Skeleton key={i} className="h-12 w-full" />
      ))}
    </div>
  );
}
