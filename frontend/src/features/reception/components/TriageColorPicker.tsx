import {
  TRIAGE_COLOR_LABELS,
  TRIAGE_COLOR_OPTIONS,
  TRIAGE_WAIT_LABELS,
} from "@/constants/reception";
import type { TriageColor } from "@/types/reception";

const INDICATOR: Record<TriageColor, string> = {
  GREEN: "bg-emerald-500",
  YELLOW: "bg-yellow-400",
  RED: "bg-red-500",
};

const SELECTED: Record<TriageColor, string> = {
  GREEN: "border-emerald-500 ring-emerald-500/20",
  YELLOW: "border-yellow-500 ring-yellow-500/20",
  RED: "border-red-500 ring-red-500/20",
};

interface TriageColorPickerProps {
  value: TriageColor | null;
  onChange: (value: TriageColor) => void;
  error?: string;
}

export function TriageColorPicker({ value, onChange, error }: TriageColorPickerProps) {
  return (
    <div className="space-y-3">
      <div>
        <p className="text-sm font-semibold text-text">Classificação de urgência</p>
        <p className="mt-0.5 text-sm text-text-muted">
          Escolha a cor que melhor reflecte o estado do paciente.
        </p>
      </div>

      <div className="grid gap-3 sm:grid-cols-3" role="radiogroup" aria-label="Cor de triagem">
        {TRIAGE_COLOR_OPTIONS.map((option) => {
          const selected = value === option.value;

          return (
            <button
              key={option.value}
              type="button"
              role="radio"
              aria-checked={selected}
              onClick={() => onChange(option.value)}
              className={`flex h-full min-h-[132px] flex-col rounded-xl border bg-surface p-4 text-left shadow-sm transition focus-ring ${
                selected
                  ? `border-2 ring-2 ${SELECTED[option.value]}`
                  : "border-border hover:border-primary-300 hover:shadow-md dark:hover:border-primary-700"
              }`}
            >
              <div className="flex items-center justify-between gap-3">
                <div className="flex min-w-0 items-center gap-2.5">
                  <span
                    className={`h-3 w-3 shrink-0 rounded-full ${INDICATOR[option.value]}`}
                    aria-hidden
                  />
                  <span className="truncate text-sm font-semibold text-text">
                    {TRIAGE_COLOR_LABELS[option.value]}
                  </span>
                </div>
                <span className="shrink-0 rounded-md bg-surface-muted px-2 py-1 text-xs font-medium text-text-muted">
                  {TRIAGE_WAIT_LABELS[option.value]}
                </span>
              </div>

              <p className="mt-1 text-xs font-medium text-text-muted">{option.summary}</p>

              <p className="mt-2 flex-1 text-sm leading-relaxed text-text-muted">
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
