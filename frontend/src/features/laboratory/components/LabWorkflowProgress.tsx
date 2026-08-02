import type { LaboratoryOrderStatus } from "@/types/laboratory";

import { getWorkflowProgress, getWorkflowStepIndex, LAB_WORKFLOW_STEPS } from "../utils/labWorkflow";

interface LabWorkflowProgressProps {
  status: LaboratoryOrderStatus;
  compact?: boolean;
}

export function LabWorkflowProgress({ status, compact }: LabWorkflowProgressProps) {
  const currentIndex = getWorkflowStepIndex(status);
  const progress = getWorkflowProgress(status);

  if (status === "CANCELADO") {
    return (
      <div className="rounded-lg bg-slate-100 px-3 py-2 text-xs font-medium text-slate-600">
        Pedido cancelado
      </div>
    );
  }

  if (compact) {
    return (
      <div className="space-y-1">
        <div className="h-1.5 overflow-hidden rounded-full bg-slate-100">
          <div
            className="h-full rounded-full bg-primary-500 transition-all"
            style={{ width: `${progress}%` }}
          />
        </div>
        <p className="text-[10px] text-slate-500">{progress}% concluído</p>
      </div>
    );
  }

  return (
    <div className="space-y-3" role="progressbar" aria-valuenow={progress} aria-valuemin={0} aria-valuemax={100}>
      <div className="h-2 overflow-hidden rounded-full bg-slate-100">
        <div
          className="h-full rounded-full bg-gradient-to-r from-primary-500 to-primary-600 transition-all duration-500"
          style={{ width: `${Math.max(progress, 8)}%` }}
        />
      </div>
      <ol className="flex justify-between gap-1">
        {LAB_WORKFLOW_STEPS.map((step, index) => {
          const isActive = index === currentIndex;
          const isComplete = index < currentIndex;
          return (
            <li
              key={step.status}
              className={`flex-1 text-center text-[10px] font-medium sm:text-xs ${
                isActive
                  ? "text-primary-700"
                  : isComplete
                    ? "text-emerald-600"
                    : "text-slate-400"
              }`}
            >
              <span
                className={`mx-auto mb-1 flex h-5 w-5 items-center justify-center rounded-full text-[10px] ${
                  isActive
                    ? "bg-primary-600 text-white ring-2 ring-primary-200"
                    : isComplete
                      ? "bg-emerald-500 text-white"
                      : "bg-slate-200 text-slate-500"
                }`}
                aria-hidden
              >
                {isComplete ? "✓" : index + 1}
              </span>
              <span className="hidden sm:inline">{step.label}</span>
            </li>
          );
        })}
      </ol>
    </div>
  );
}
