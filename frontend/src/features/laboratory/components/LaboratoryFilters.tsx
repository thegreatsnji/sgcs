import { LAB_FATURACAO_LABELS, LAB_STATUS_LABELS } from "@/constants/laboratory";
import { PRIORITY_LABELS } from "@/constants/appointments";

interface LaboratoryFiltersProps {
  search: string;
  onSearchChange: (value: string) => void;
  estado: string;
  onEstadoChange: (value: string) => void;
  prioridade: string;
  onPrioridadeChange: (value: string) => void;
  dataPedido: string;
  onDataPedidoChange: (value: string) => void;
  estadoFaturacao: string;
  onEstadoFaturacaoChange: (value: string) => void;
}

export function LaboratoryFilters({
  search,
  onSearchChange,
  estado,
  onEstadoChange,
  prioridade,
  onPrioridadeChange,
  dataPedido,
  onDataPedidoChange,
  estadoFaturacao,
  onEstadoFaturacaoChange,
}: LaboratoryFiltersProps) {
  return (
    <div className="flex flex-wrap items-end gap-3 rounded-2xl border border-slate-200/80 bg-white p-4 shadow-sm">
      <div className="min-w-[200px] flex-1">
        <label htmlFor="lab-search" className="mb-1 block text-sm font-medium text-slate-700">
          Pesquisar
        </label>
        <input
          id="lab-search"
          type="search"
          value={search}
          onChange={(e) => onSearchChange(e.target.value)}
          placeholder="Utente, código, exame ou pedido…"
          className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
        />
      </div>
      <div>
        <label htmlFor="lab-estado" className="mb-1 block text-sm font-medium text-slate-700">
          Estado
        </label>
        <select
          id="lab-estado"
          value={estado}
          onChange={(e) => onEstadoChange(e.target.value)}
          className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
        >
          <option value="">Todos</option>
          {Object.entries(LAB_STATUS_LABELS).map(([value, label]) => (
            <option key={value} value={value}>
              {label}
            </option>
          ))}
        </select>
      </div>
      <div>
        <label htmlFor="lab-prio" className="mb-1 block text-sm font-medium text-slate-700">
          Prioridade
        </label>
        <select
          id="lab-prio"
          value={prioridade}
          onChange={(e) => onPrioridadeChange(e.target.value)}
          className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
        >
          <option value="">Todas</option>
          {Object.entries(PRIORITY_LABELS).map(([value, label]) => (
            <option key={value} value={value}>
              {label}
            </option>
          ))}
        </select>
      </div>
      <div>
        <label htmlFor="lab-data" className="mb-1 block text-sm font-medium text-slate-700">
          Data
        </label>
        <input
          id="lab-data"
          type="date"
          value={dataPedido}
          onChange={(e) => onDataPedidoChange(e.target.value)}
          className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
        />
      </div>
      <div>
        <label htmlFor="lab-fat" className="mb-1 block text-sm font-medium text-slate-700">
          Regularização
        </label>
        <select
          id="lab-fat"
          value={estadoFaturacao}
          onChange={(e) => onEstadoFaturacaoChange(e.target.value)}
          className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
        >
          <option value="">Todas</option>
          <option value="AGUARDA_REGULARIZACAO">{LAB_FATURACAO_LABELS.AGUARDA_REGULARIZACAO}</option>
          <option value="REGULARIZADO">{LAB_FATURACAO_LABELS.REGULARIZADO}</option>
        </select>
      </div>
    </div>
  );
}
