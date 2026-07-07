import type { ReportPeriod } from "@/types/reports";

interface ReportFilterProps {
  periodo: ReportPeriod;
  onPeriodoChange: (p: ReportPeriod) => void;
}

const options: Array<{ value: ReportPeriod; label: string }> = [
  { value: "hoje", label: "Hoje" },
  { value: "semana", label: "Semana" },
  { value: "mes", label: "Mês" },
  { value: "ano", label: "Ano" },
  { value: "personalizado", label: "Personalizado" },
];

export function ReportFilter({ periodo, onPeriodoChange }: ReportFilterProps) {
  return (
    <div className="flex flex-wrap items-center gap-2">
      <span className="text-sm text-slate-600">Período:</span>
      {options.map((o) => (
        <button
          key={o.value}
          type="button"
          onClick={() => onPeriodoChange(o.value)}
          className={`rounded-lg px-3 py-1.5 text-sm ${periodo === o.value ? "bg-primary-600 text-white" : "border border-slate-300 text-slate-700"}`}
        >
          {o.label}
        </button>
      ))}
    </div>
  );
}
