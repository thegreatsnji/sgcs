import { LAB_STATUS_LABELS } from "@/constants/laboratory";

interface LaboratoryFiltersProps {
  estado: string;
  onEstadoChange: (value: string) => void;
}

export function LaboratoryFilters({ estado, onEstadoChange }: LaboratoryFiltersProps) {
  return (
    <div className="flex flex-wrap items-end gap-4">
      <div>
        <label className="mb-1 block text-sm font-medium text-slate-700">Estado</label>
        <select
          value={estado}
          onChange={(e) => onEstadoChange(e.target.value)}
          className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
        >
          <option value="">Todos</option>
          {Object.entries(LAB_STATUS_LABELS).map(([value, label]) => (
            <option key={value} value={value}>{label}</option>
          ))}
        </select>
      </div>
    </div>
  );
}
