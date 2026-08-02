import { IconCalendar, IconPatients, IconSearch } from "@/components/icons";

type WizardStep = "search" | "register" | "triage";

const STEPS: { id: WizardStep; label: string; short: string; icon: typeof IconSearch }[] = [
  { id: "search", label: "Pesquisar paciente", short: "Pesquisar", icon: IconSearch },
  { id: "register", label: "Registo rápido", short: "Registar", icon: IconPatients },
  { id: "triage", label: "Triagem clínica", short: "Triagem", icon: IconCalendar },
];

function stepIndex(step: WizardStep): number {
  return STEPS.findIndex((item) => item.id === step);
}

interface TriageWizardStepsProps {
  current: WizardStep;
}

export function TriageWizardSteps({ current }: TriageWizardStepsProps) {
  const currentIndex = stepIndex(current);

  return (
    <nav aria-label="Progresso da triagem" className="rounded-2xl border border-border bg-surface p-4 shadow-sm sm:p-6">
      <ol className="flex items-center">
        {STEPS.map((item, index) => {
          const Icon = item.icon;
          const isComplete = index < currentIndex;
          const isCurrent = index === currentIndex;
          const isUpcoming = index > currentIndex;

          return (
            <li key={item.id} className={`flex items-center ${index < STEPS.length - 1 ? "flex-1" : ""}`}>
              <div className="flex min-w-0 flex-col items-center gap-2 sm:flex-row sm:gap-3">
                <span
                  className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-full border-2 text-sm font-bold transition ${
                    isComplete
                      ? "border-primary-600 bg-primary-600 text-white"
                      : isCurrent
                        ? "border-primary-600 bg-primary-50 text-primary-700 dark:bg-primary-950 dark:text-primary-300"
                        : "border-border bg-surface-muted text-text-muted"
                  }`}
                  aria-current={isCurrent ? "step" : undefined}
                >
                  {isComplete ? (
                    <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
                    </svg>
                  ) : (
                    <Icon className="h-5 w-5" />
                  )}
                </span>
                <div className="hidden min-w-0 text-center sm:block sm:text-left">
                  <p
                    className={`text-sm font-semibold ${
                      isCurrent ? "text-text" : isUpcoming ? "text-text-muted" : "text-primary-700 dark:text-primary-300"
                    }`}
                  >
                    <span className="sm:hidden">{item.short}</span>
                    <span className="hidden sm:inline">{item.label}</span>
                  </p>
                  <p className="text-xs text-text-muted">
                    Passo {index + 1} de {STEPS.length}
                  </p>
                </div>
              </div>

              {index < STEPS.length - 1 && (
                <div
                  className={`mx-2 hidden h-0.5 flex-1 sm:mx-4 sm:block ${
                    index < currentIndex ? "bg-primary-500" : "bg-border"
                  }`}
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

export type { WizardStep };
