import { RECEPTION_ATENDIMENTO_STEPS, type ReceptionAtendimentoStepId } from "@/features/reception/constants/atendimentoSteps";

interface ReceptionAtendimentoStepperProps {
  current: ReceptionAtendimentoStepId;
  maxReachable?: ReceptionAtendimentoStepId;
  onStepClick?: (step: ReceptionAtendimentoStepId) => void;
}

export function ReceptionAtendimentoStepper({
  current,
  maxReachable = current,
  onStepClick,
}: ReceptionAtendimentoStepperProps) {
  return (
    <nav aria-label="Passos do atendimento" className="rounded-2xl border border-border bg-surface p-3 shadow-sm sm:p-4">
      <ol className="flex flex-wrap items-center justify-between gap-2 sm:flex-nowrap sm:gap-0">
        {RECEPTION_ATENDIMENTO_STEPS.map((step, index) => {
          const isComplete = step.id < current;
          const isCurrent = step.id === current;
          const canNavigate = step.id <= maxReachable && onStepClick;

          return (
            <li
              key={step.id}
              className={`flex min-w-[4.5rem] flex-1 items-center ${index < RECEPTION_ATENDIMENTO_STEPS.length - 1 ? "sm:flex-1" : ""}`}
            >
              <button
                type="button"
                disabled={!canNavigate}
                onClick={() => canNavigate && onStepClick(step.id)}
                className={`flex w-full flex-col items-center gap-1 rounded-lg px-1 py-1 text-center transition focus-ring disabled:cursor-default ${
                  canNavigate ? "hover:bg-surface-muted" : ""
                }`}
                aria-current={isCurrent ? "step" : undefined}
              >
                <span
                  className={`flex h-9 w-9 items-center justify-center rounded-full text-xs font-bold ${
                    isComplete
                      ? "bg-emerald-600 text-white"
                      : isCurrent
                        ? "bg-primary-600 text-white ring-2 ring-primary-200"
                        : step.id <= maxReachable
                          ? "bg-surface-muted text-text"
                          : "bg-surface-muted/60 text-text-muted"
                  }`}
                >
                  {isComplete ? "✓" : step.id}
                </span>
                <span
                  className={`text-[10px] font-semibold leading-tight sm:text-xs ${
                    isCurrent ? "text-text" : "text-text-muted"
                  }`}
                >
                  <span className="sm:hidden">{step.short}</span>
                  <span className="hidden sm:inline">{step.label}</span>
                </span>
              </button>
              {index < RECEPTION_ATENDIMENTO_STEPS.length - 1 && (
                <div
                  className={`mx-1 hidden h-0.5 flex-1 sm:block ${step.id < current ? "bg-emerald-500" : "bg-border"}`}
                  aria-hidden
                />
              )}
            </li>
          );
        })}
      </ol>
    </nav>
  );
}
