import { Button } from "@/design-system";
import type { ParametroResultado } from "@/types/laboratoryResult";

const emptyRow = (): ParametroResultado => ({
  nome: "",
  valor: "",
  unidade: "",
  valor_minimo: "",
  valor_maximo: "",
  interpretacao: "NORMAL",
});

interface ParametroEditorProps {
  value: ParametroResultado[];
  onChange: (rows: ParametroResultado[]) => void;
  disabled?: boolean;
}

export function ParametroEditor({ value, onChange, disabled }: ParametroEditorProps) {
  const rows = value.length ? value : [emptyRow()];

  const update = (index: number, field: keyof ParametroResultado, val: string) => {
    const next = rows.map((row, i) => (i === index ? { ...row, [field]: val } : row));
    onChange(next);
  };

  const addRow = () => onChange([...rows, emptyRow()]);
  const removeRow = (index: number) => onChange(rows.filter((_, i) => i !== index));

  return (
    <div className="space-y-3">
      <div className="hidden gap-2 text-xs font-medium text-slate-500 md:grid md:grid-cols-6">
        <span>Parâmetro</span>
        <span>Valor</span>
        <span>Unidade</span>
        <span>Mínimo</span>
        <span>Máximo</span>
        <span />
      </div>
      {rows.map((row, index) => (
        <div key={index} className="grid gap-2 rounded-lg border border-slate-200 p-3 md:grid-cols-6">
          <input
            className="rounded border border-slate-300 px-2 py-1.5 text-sm"
            placeholder="Nome"
            value={row.nome}
            disabled={disabled}
            onChange={(e) => update(index, "nome", e.target.value)}
          />
          <input
            className="rounded border border-slate-300 px-2 py-1.5 text-sm"
            placeholder="Valor"
            value={row.valor}
            disabled={disabled}
            onChange={(e) => update(index, "valor", e.target.value)}
          />
          <input
            className="rounded border border-slate-300 px-2 py-1.5 text-sm"
            placeholder="Unidade"
            value={row.unidade}
            disabled={disabled}
            onChange={(e) => update(index, "unidade", e.target.value)}
          />
          <input
            className="rounded border border-slate-300 px-2 py-1.5 text-sm"
            placeholder="Mín."
            value={row.valor_minimo}
            disabled={disabled}
            onChange={(e) => update(index, "valor_minimo", e.target.value)}
          />
          <input
            className="rounded border border-slate-300 px-2 py-1.5 text-sm"
            placeholder="Máx."
            value={row.valor_maximo}
            disabled={disabled}
            onChange={(e) => update(index, "valor_maximo", e.target.value)}
          />
          {!disabled && (
            <Button type="button" variant="ghost" onClick={() => removeRow(index)}>
              Remover
            </Button>
          )}
        </div>
      ))}
      {!disabled && (
        <Button type="button" variant="secondary" onClick={addRow}>
          Adicionar parâmetro
        </Button>
      )}
    </div>
  );
}
