interface DateRangePickerProps {
  inicio: string;
  fim: string;
  onChange: (inicio: string, fim: string) => void;
}

export function DateRangePicker({ inicio, fim, onChange }: DateRangePickerProps) {
  return (
    <div className="flex flex-wrap items-center gap-2">
      <input
        type="date"
        value={inicio}
        onChange={(e) => onChange(e.target.value, fim)}
        className="rounded border border-slate-300 px-2 py-1 text-sm"
      />
      <span className="text-slate-500">até</span>
      <input
        type="date"
        value={fim}
        onChange={(e) => onChange(inicio, e.target.value)}
        className="rounded border border-slate-300 px-2 py-1 text-sm"
      />
    </div>
  );
}
