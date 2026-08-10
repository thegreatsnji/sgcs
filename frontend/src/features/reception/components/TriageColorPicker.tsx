import { TRIAGE_COLOR_OPTIONS } from "@/constants/reception";
import type { TriageColor } from "@/types/reception";

const SWATCH: Record<TriageColor, { fill: string; ring: string; border: string; tint: string }> = {
  GREEN: {
    fill: "bg-emerald-500",
    ring: "ring-emerald-500/35",
    border: "border-emerald-500",
    tint: "bg-emerald-50/80 dark:bg-emerald-950/25",
  },
  YELLOW: {
    fill: "bg-amber-400",
    ring: "ring-amber-400/40",
    border: "border-amber-500",
    tint: "bg-amber-50/80 dark:bg-amber-950/25",
  },
  RED: {
    fill: "bg-red-500",
    ring: "ring-red-500/35",
    border: "border-red-500",
    tint: "bg-red-50/80 dark:bg-red-950/25",
  },
};

interface TriageColorPickerProps {
  value: TriageColor | null;
  onChange: (value: TriageColor) => void;
  error?: string;
}

export function TriageColorPicker({ value, onChange, error }: TriageColorPickerProps) {
  return (
    <div className="space-y-4 text-center">
      <div>
        <p className="text-sm font-semibold text-text">Cor de triagem</p>
        <p className="mt-0.5 text-sm text-text-muted">
          Escolha a cor que melhor reflecte o estado do paciente.
        </p>
      </div>

      <div className="grid gap-3 sm:grid-cols-3" role="radiogroup" aria-label="Cor de triagem">
        {TRIAGE_COLOR_OPTIONS.map((option) => {
          const selected = value === option.value;
          const swatch = SWATCH[option.value];

          return (
            <button
              key={option.value}
              type="button"
              role="radio"
              aria-checked={selected}
              onClick={() => onChange(option.value)}
              className={`flex h-full flex-col items-center rounded-2xl border p-5 text-center shadow-sm transition focus-ring ${
                selected
                  ? `border-2 ${swatch.border} ring-2 ${swatch.ring} ${swatch.tint}`
                  : "border-border bg-surface hover:border-primary-300 hover:shadow-md dark:hover:border-primary-700"
              }`}
            >
              <span
                className={`h-9 w-14 shrink-0 rounded-full border-2 transition ${
                  selected
                    ? `${swatch.fill} ${swatch.border} ring-2 ring-offset-2 ring-offset-surface ${swatch.ring}`
                    : `border-border bg-surface ${swatch.border}/40`
                }`}
                aria-hidden
              />

              <span className="mt-3 rounded-lg bg-surface-muted px-2.5 py-1 text-xs font-semibold text-text-muted">
                {option.waitLabel}
              </span>

              <p className="mt-3 text-base font-semibold leading-snug text-text">{option.summary}</p>
              <p className="mt-1 text-xs font-medium text-text-muted">{option.label}</p>

              <p className="mt-2 max-w-[16rem] text-sm leading-relaxed text-text-muted">
                {option.description}
              </p>
            </button>
          );
        })}
      </div>

      {error && <p className="text-sm text-red-600 dark:text-red-400">{error}</p>}
    </div>
  );
}
