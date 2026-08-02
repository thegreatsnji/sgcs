import { Button } from "@/design-system";
import { INTERPRETACAO_COLORS, INTERPRETACAO_LABELS } from "@/constants/laboratoryResults";
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

function interpretacaoFromValue(
  valor: string,
  min: string,
  max: string,
): ParametroResultado["interpretacao"] {
  const num = parseFloat(valor);
  const minN = parseFloat(min);
  const maxN = parseFloat(max);
  if (Number.isNaN(num) || Number.isNaN(minN) || Number.isNaN(maxN)) return "NORMAL";
  if (num > maxN * 1.2) return "CRITICO";
  if (num > maxN) return "ALTO";
  if (num < minN) return "BAIXO";
  return "NORMAL";
}

export function ParametroEditor({ value, onChange, disabled }: ParametroEditorProps) {
  const rows = value.length ? value : [emptyRow()];

  const update = (index: number, field: keyof ParametroResultado, val: string) => {
    const next = rows.map((row, i) => {
      if (i !== index) return row;
      const updated = { ...row, [field]: val };
      if (field === "valor" || field === "valor_minimo" || field === "valor_maximo") {
        updated.interpretacao = interpretacaoFromValue(
          field === "valor" ? val : updated.valor,
          field === "valor_minimo" ? val : updated.valor_minimo,
          field === "valor_maximo" ? val : updated.valor_maximo,
        );
      }
      return updated;
    });
    onChange(next);
  };

  const addRow = () => onChange([...rows, emptyRow()]);
  const removeRow = (index: number) => onChange(rows.filter((_, i) => i !== index));

  return (
    <div className="rounded-2xl border border-slate-200/80 bg-white shadow-sm">
      <div className="border-b border-slate-100 px-5 py-4">
        <h3 className="text-sm font-semibold text-slate-900">Parâmetros analíticos</h3>
        <p className="mt-0.5 text-xs text-slate-500">Introduza valores e intervalos de referência</p>
      </div>

      <div className="overflow-x-auto p-4">
        <table className="min-w-full text-sm">
          <thead>
            <tr className="border-b border-slate-100 text-left text-[10px] font-semibold tracking-wide text-slate-400 uppercase">
              <th className="pb-3 pr-3">Parâmetro</th>
              <th className="pb-3 pr-3">Valor</th>
              <th className="pb-3 pr-3">Unidade</th>
              <th className="pb-3 pr-3">Referência</th>
              <th className="pb-3 pr-3">Interpretação</th>
              <th className="pb-3" />
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-50">
            {rows.map((row, index) => {
              const interp = row.interpretacao || "NORMAL";
              const colorClass = INTERPRETACAO_COLORS[interp] ?? INTERPRETACAO_COLORS.NORMAL;
              return (
                <tr key={index} className="group">
                  <td className="py-2 pr-3">
                    <input
                      className="w-full min-w-[120px] rounded-lg border border-slate-200 px-2.5 py-2 text-sm focus:border-primary-300 focus:ring-1 focus:ring-primary-100 focus:outline-none"
                      placeholder="Nome"
                      value={row.nome}
                      disabled={disabled}
                      onChange={(e) => update(index, "nome", e.target.value)}
                    />
                  </td>
                  <td className="py-2 pr-3">
                    <input
                      className="w-full min-w-[80px] rounded-lg border border-slate-200 px-2.5 py-2 text-sm font-medium focus:border-primary-300 focus:ring-1 focus:ring-primary-100 focus:outline-none"
                      placeholder="0.0"
                      value={row.valor}
                      disabled={disabled}
                      onChange={(e) => update(index, "valor", e.target.value)}
                    />
                  </td>
                  <td className="py-2 pr-3">
                    <input
                      className="w-full min-w-[60px] rounded-lg border border-slate-200 px-2.5 py-2 text-sm focus:border-primary-300 focus:ring-1 focus:ring-primary-100 focus:outline-none"
                      placeholder="g/L"
                      value={row.unidade}
                      disabled={disabled}
                      onChange={(e) => update(index, "unidade", e.target.value)}
                    />
                  </td>
                  <td className="py-2 pr-3">
                    <div className="flex items-center gap-1">
                      <input
                        className="w-16 rounded-lg border border-slate-200 px-2 py-2 text-xs focus:border-primary-300 focus:outline-none"
                        placeholder="Mín"
                        value={row.valor_minimo}
                        disabled={disabled}
                        onChange={(e) => update(index, "valor_minimo", e.target.value)}
                      />
                      <span className="text-slate-300">–</span>
                      <input
                        className="w-16 rounded-lg border border-slate-200 px-2 py-2 text-xs focus:border-primary-300 focus:outline-none"
                        placeholder="Máx"
                        value={row.valor_maximo}
                        disabled={disabled}
                        onChange={(e) => update(index, "valor_maximo", e.target.value)}
                      />
                    </div>
                  </td>
                  <td className="py-2 pr-3">
                    <span
                      className={`inline-flex rounded-lg border px-2.5 py-1 text-xs font-semibold ${colorClass}`}
                    >
                      {INTERPRETACAO_LABELS[interp] ?? interp}
                    </span>
                  </td>
                  <td className="py-2">
                    {!disabled && (
                      <Button type="button" variant="ghost" size="sm" onClick={() => removeRow(index)}>
                        ×
                      </Button>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {!disabled && (
        <div className="border-t border-slate-100 px-5 py-3">
          <Button type="button" variant="secondary" size="sm" onClick={addRow}>
            + Adicionar parâmetro
          </Button>
        </div>
      )}
    </div>
  );
}
