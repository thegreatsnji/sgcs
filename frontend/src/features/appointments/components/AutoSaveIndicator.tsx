interface AutoSaveIndicatorProps {
  isSaving: boolean;
  lastSaved?: Date | null;
}

export function AutoSaveIndicator({ isSaving, lastSaved }: AutoSaveIndicatorProps) {
  return (
    <div
      className="inline-flex items-center gap-2 rounded-full border border-slate-200 bg-white px-3 py-1.5 text-xs font-medium text-slate-600 shadow-sm"
      role="status"
      aria-live="polite"
    >
      <span
        className={`h-2 w-2 rounded-full ${isSaving ? "animate-pulse bg-amber-400" : "bg-emerald-500"}`}
        aria-hidden
      />
      {isSaving ? "A guardar..." : lastSaved ? `Guardado às ${lastSaved.toLocaleTimeString("pt-PT", { hour: "2-digit", minute: "2-digit" })}` : "Todas as alterações guardadas"}
    </div>
  );
}
