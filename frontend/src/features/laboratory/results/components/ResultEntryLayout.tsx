import { Avatar } from "@/design-system";
import { ResultadoStatusBadge } from "@/features/laboratory/results/components/ResultadoStatusBadge";
import type { LaboratoryResult } from "@/types/laboratoryResult";

export interface LabPatientInfo {
  full_name: string;
  patient_number?: string;
  gender_label?: string | null;
  birth_date?: string | null;
  age_years?: number | null;
  numero_pedido?: string;
  medico_nome?: string | null;
  consulta_id?: number;
  estado?: LaboratoryResult["estado"];
}

interface LabPatientPanelProps {
  patient: LabPatientInfo;
}

export function LabPatientPanel({ patient }: LabPatientPanelProps) {
  return (
    <aside className="rounded-2xl border border-slate-200/80 bg-white p-5 shadow-sm xl:sticky xl:top-20">
      <div className="flex flex-col items-center text-center">
        <Avatar name={patient.full_name} size="lg" />
        <h2 className="mt-3 text-lg font-bold text-slate-900">{patient.full_name}</h2>
        {patient.patient_number && (
          <p className="font-mono text-xs text-slate-500">{patient.patient_number}</p>
        )}
      </div>

      <dl className="mt-6 space-y-4 border-t border-slate-100 pt-6 text-sm">
        {patient.numero_pedido && (
          <div>
            <dt className="text-[10px] font-semibold tracking-widest text-slate-400 uppercase">N.º Pedido</dt>
            <dd className="mt-1 font-mono font-medium text-slate-900">{patient.numero_pedido}</dd>
          </div>
        )}
        {patient.medico_nome && (
          <div>
            <dt className="text-[10px] font-semibold tracking-widest text-slate-400 uppercase">Médico</dt>
            <dd className="mt-1 text-slate-700">{patient.medico_nome}</dd>
          </div>
        )}
        {patient.estado && (
          <div>
            <dt className="text-[10px] font-semibold tracking-widest text-slate-400 uppercase">Estado</dt>
            <dd className="mt-2">
              <ResultadoStatusBadge status={patient.estado} />
            </dd>
          </div>
        )}
      </dl>
    </aside>
  );
}

interface InterpretationPanelProps {
  observacoes: string;
  conclusao: string;
  onObservacoesChange?: (value: string) => void;
  onConclusaoChange?: (value: string) => void;
  disabled?: boolean;
  timeline?: React.ReactNode;
  validationStatus?: React.ReactNode;
}

export function InterpretationPanel({
  observacoes,
  conclusao,
  onObservacoesChange,
  onConclusaoChange,
  disabled,
  timeline,
  validationStatus,
}: InterpretationPanelProps) {
  const isEditable = Boolean(onObservacoesChange);

  return (
    <aside className="space-y-4 xl:sticky xl:top-20 xl:self-start">
      {validationStatus}

      <div className="rounded-2xl border border-slate-200/80 bg-white p-5 shadow-sm">
        <h3 className="text-sm font-semibold text-slate-900">Interpretação clínica</h3>

        <div className="mt-4 space-y-4">
          <div>
            <label className="mb-1.5 block text-[10px] font-semibold tracking-widest text-slate-400 uppercase">
              Observações
            </label>
            {isEditable ? (
              <textarea
                className="min-h-24 w-full rounded-xl border border-slate-200 bg-slate-50/50 px-3 py-2 text-sm transition focus:border-primary-300 focus:bg-white focus:ring-2 focus:ring-primary-100 focus:outline-none"
                value={observacoes}
                disabled={disabled}
                onChange={(e) => onObservacoesChange?.(e.target.value)}
              />
            ) : (
              <p className="text-sm text-slate-700">{observacoes || "—"}</p>
            )}
          </div>

          <div>
            <label className="mb-1.5 block text-[10px] font-semibold tracking-widest text-slate-400 uppercase">
              Conclusão
            </label>
            {isEditable ? (
              <textarea
                className="min-h-24 w-full rounded-xl border border-slate-200 bg-slate-50/50 px-3 py-2 text-sm transition focus:border-primary-300 focus:bg-white focus:ring-2 focus:ring-primary-100 focus:outline-none"
                value={conclusao}
                disabled={disabled}
                onChange={(e) => onConclusaoChange?.(e.target.value)}
              />
            ) : (
              <p className="text-sm text-slate-700">{conclusao || "—"}</p>
            )}
          </div>
        </div>
      </div>

      {timeline && (
        <div className="rounded-2xl border border-slate-200/80 bg-white p-5 shadow-sm">
          <h3 className="mb-4 text-sm font-semibold text-slate-900">Linha do tempo</h3>
          {timeline}
        </div>
      )}
    </aside>
  );
}
