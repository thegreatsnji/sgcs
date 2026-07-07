interface NotificationFiltersProps {
  filtro: string;
  onChange: (valor: string) => void;
}

const opcoes = [
  { value: "todas", label: "Todas" },
  { value: "nao_lidas", label: "Não lidas" },
  { value: "lidas", label: "Lidas" },
  { value: "urgente", label: "Urgentes" },
];

export function NotificationFilters({ filtro, onChange }: NotificationFiltersProps) {
  return (
    <div className="flex flex-wrap gap-2">
      {opcoes.map((op) => (
        <button
          key={op.value}
          type="button"
          className={`rounded-full px-3 py-1 text-sm ${
            filtro === op.value ? "bg-primary-600 text-white" : "bg-slate-100 text-slate-600"
          }`}
          onClick={() => onChange(op.value)}
        >
          {op.label}
        </button>
      ))}
    </div>
  );
}
