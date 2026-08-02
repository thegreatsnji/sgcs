import { useState } from "react";

import { Button } from "@/design-system";
import { ParametroEditor } from "@/features/laboratory/results/components/ParametroEditor";
import {
  InterpretationPanel,
  LabPatientPanel,
  type LabPatientInfo,
} from "@/features/laboratory/results/components/ResultEntryLayout";
import type { ParametroResultado } from "@/types/laboratoryResult";

export interface ResultadoFormValues {
  pedido_laboratorial: number;
  observacoes: string;
  conclusao: string;
  parametros: ParametroResultado[];
}

interface ResultadoFormProps {
  initial?: Partial<ResultadoFormValues>;
  patientInfo?: LabPatientInfo;
  onSubmit: (values: ResultadoFormValues) => void;
  isPending?: boolean;
  disabled?: boolean;
  showPedidoField?: boolean;
  parametersReadOnly?: boolean;
}

export function ResultadoForm({
  initial,
  patientInfo,
  onSubmit,
  isPending,
  disabled,
  showPedidoField = false,
  parametersReadOnly = false,
}: ResultadoFormProps) {
  const [pedidoId, setPedidoId] = useState(initial?.pedido_laboratorial ?? 0);
  const [observacoes, setObservacoes] = useState(initial?.observacoes ?? "");
  const [conclusao, setConclusao] = useState(initial?.conclusao ?? "");
  const [parametros, setParametros] = useState<ParametroResultado[]>(initial?.parametros ?? []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({
      pedido_laboratorial: pedidoId,
      observacoes,
      conclusao,
      parametros: parametros.filter((p) => p.nome && p.valor),
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {showPedidoField && (
        <div className="rounded-2xl border border-slate-200/80 bg-white p-5 shadow-sm">
          <label className="mb-1.5 block text-sm font-medium text-slate-700">ID do pedido laboratorial</label>
          <input
            type="number"
            className="w-full max-w-xs rounded-xl border border-slate-200 px-3 py-2 text-sm focus:border-primary-300 focus:ring-2 focus:ring-primary-100 focus:outline-none"
            value={pedidoId || ""}
            disabled={disabled}
            onChange={(e) => setPedidoId(Number(e.target.value))}
            required
          />
        </div>
      )}

      <div className="grid gap-6 xl:grid-cols-[240px_1fr_280px]">
        {patientInfo && (
          <LabPatientPanel patient={patientInfo} />
        )}

        <div className="min-w-0 space-y-4">
          <ParametroEditor value={parametros} onChange={setParametros} disabled={disabled || parametersReadOnly} />
        </div>

        <InterpretationPanel
          observacoes={observacoes}
          conclusao={conclusao}
          onObservacoesChange={disabled ? undefined : setObservacoes}
          onConclusaoChange={disabled ? undefined : setConclusao}
          disabled={disabled}
        />
      </div>

      {!disabled && (
        <div className="sticky bottom-0 z-10 -mx-4 border-t border-slate-200 bg-white/95 px-4 py-4 backdrop-blur-md lg:-mx-0 lg:rounded-2xl lg:border lg:shadow-sm">
          <Button type="submit" variant="primary" size="lg" disabled={isPending} isLoading={isPending}>
            Guardar resultado
          </Button>
        </div>
      )}
    </form>
  );
}
