import { Button, Card } from "@/design-system";
import { isAbnormalBloodPressure, isAbnormalVital } from "@/features/appointments/utils/vitals";
import type { VitalSigns } from "@/types/clinicalRecord";

interface SinaisVitaisFormProps {
  initial?: VitalSigns | null;
  triage?: VitalSigns | null;
  disabled?: boolean;
  onSubmit: (data: Partial<VitalSigns>) => void;
  isPending?: boolean;
}

function VitalField({
  label,
  value,
  abnormal,
  children,
}: {
  label: string;
  value?: string;
  abnormal?: boolean;
  children: React.ReactNode;
}) {
  return (
    <div>
      <label className={`mb-1 block text-sm font-medium ${abnormal ? "text-red-700" : "text-slate-700"}`}>
        {label}
        {abnormal && value && <span className="ml-1 text-xs">(fora do normal)</span>}
      </label>
      {children}
    </div>
  );
}

export function SinaisVitaisForm({ initial, triage, disabled, onSubmit, isPending }: SinaisVitaisFormProps) {
  const imc = initial?.imc;

  return (
    <Card title="Sinais vitais">
      {triage ? (
        <div className="mb-4 rounded-lg border border-slate-200 bg-slate-50 p-3 text-sm text-slate-700">
          <p className="font-medium text-slate-800">Sinais vitais da triagem</p>
          <p className="mt-1 text-xs text-slate-500">Referência do check-in — não substitui o registo clínico.</p>
        </div>
      ) : null}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          const fd = new FormData(e.currentTarget);
          onSubmit({
            pressao_arterial: String(fd.get("pressao_arterial") ?? ""),
            frequencia_cardiaca: fd.get("frequencia_cardiaca")
              ? Number(fd.get("frequencia_cardiaca"))
              : null,
            frequencia_respiratoria: fd.get("frequencia_respiratoria")
              ? Number(fd.get("frequencia_respiratoria"))
              : null,
            temperatura: fd.get("temperatura") ? Number(fd.get("temperatura")) : null,
            saturacao_oxigenio: fd.get("saturacao_oxigenio")
              ? Number(fd.get("saturacao_oxigenio"))
              : null,
            peso: fd.get("peso") ? Number(fd.get("peso")) : null,
            altura: fd.get("altura") ? Number(fd.get("altura")) : null,
            observacoes: String(fd.get("observacoes") ?? ""),
          });
        }}
        className="grid gap-4 sm:grid-cols-2"
      >
        <VitalField
          label="Pressão arterial"
          value={initial?.pressao_arterial}
          abnormal={isAbnormalBloodPressure(initial?.pressao_arterial ?? "")}
        >
          <input
            name="pressao_arterial"
            defaultValue={initial?.pressao_arterial ?? ""}
            placeholder="120/80"
            disabled={disabled}
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm disabled:bg-slate-50"
          />
        </VitalField>
        <VitalField
          label="FC (bpm)"
          abnormal={isAbnormalVital("frequencia_cardiaca", initial?.frequencia_cardiaca)}
        >
          <input
            name="frequencia_cardiaca"
            type="number"
            defaultValue={initial?.frequencia_cardiaca ?? ""}
            disabled={disabled}
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm disabled:bg-slate-50"
          />
        </VitalField>
        <VitalField
          label="FR (rpm)"
          abnormal={isAbnormalVital("frequencia_respiratoria", initial?.frequencia_respiratoria)}
        >
          <input
            name="frequencia_respiratoria"
            type="number"
            defaultValue={initial?.frequencia_respiratoria ?? ""}
            disabled={disabled}
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm disabled:bg-slate-50"
          />
        </VitalField>
        <VitalField
          label="Temperatura (°C)"
          abnormal={isAbnormalVital("temperatura", initial?.temperatura)}
        >
          <input
            name="temperatura"
            type="number"
            step="0.1"
            defaultValue={initial?.temperatura ?? ""}
            disabled={disabled}
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm disabled:bg-slate-50"
          />
        </VitalField>
        <VitalField
          label="SpO₂ (%)"
          abnormal={isAbnormalVital("saturacao_oxigenio", initial?.saturacao_oxigenio)}
        >
          <input
            name="saturacao_oxigenio"
            type="number"
            defaultValue={initial?.saturacao_oxigenio ?? ""}
            disabled={disabled}
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm disabled:bg-slate-50"
          />
        </VitalField>
        <VitalField label="Peso (kg)">
          <input
            name="peso"
            type="number"
            step="0.1"
            defaultValue={initial?.peso ?? ""}
            disabled={disabled}
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm disabled:bg-slate-50"
          />
        </VitalField>
        <VitalField label="Altura (cm)">
          <input
            name="altura"
            type="number"
            step="0.1"
            defaultValue={initial?.altura ?? ""}
            disabled={disabled}
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm disabled:bg-slate-50"
          />
        </VitalField>
        <div>
          <label className="mb-1 block text-sm font-medium text-slate-700">IMC (calculado)</label>
          <p
            className={`rounded-lg border px-3 py-2 text-sm ${
              isAbnormalVital("imc", imc) ? "border-red-300 bg-red-50 text-red-800" : "border-slate-200 bg-slate-50"
            }`}
          >
            {imc != null ? imc.toFixed(2) : "—"}
          </p>
        </div>
        <div className="sm:col-span-2">
          <label className="mb-1 block text-sm font-medium text-slate-700">Observações</label>
          <textarea
            name="observacoes"
            rows={2}
            defaultValue={initial?.observacoes ?? ""}
            disabled={disabled}
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm disabled:bg-slate-50"
          />
        </div>
        {!disabled && (
          <div className="sm:col-span-2">
            <Button type="submit" disabled={isPending}>
              Guardar sinais vitais
            </Button>
          </div>
        )}
      </form>
    </Card>
  );
}
