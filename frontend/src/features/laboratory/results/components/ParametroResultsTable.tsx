import { INTERPRETACAO_COLORS, INTERPRETACAO_LABELS } from "@/constants/laboratoryResults";
import type { ParametroResultado } from "@/types/laboratoryResult";

interface ParametroResultsTableProps {
  parametros: ParametroResultado[];
}

export function ParametroResultsTable({ parametros }: ParametroResultsTableProps) {
  if (parametros.length === 0) {
    return (
      <p className="rounded-xl border border-dashed border-slate-200 p-8 text-center text-sm text-slate-500">
        Sem parâmetros registados.
      </p>
    );
  }

  return (
    <div className="overflow-hidden rounded-2xl border border-slate-200/80 bg-white shadow-sm">
      <div className="border-b border-slate-100 px-5 py-4">
        <h3 className="text-sm font-semibold text-slate-900">Resultados analíticos</h3>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full text-sm">
          <thead className="bg-slate-50/80">
            <tr className="text-left text-[10px] font-semibold tracking-wide text-slate-400 uppercase">
              <th className="px-5 py-3">Parâmetro</th>
              <th className="px-5 py-3">Valor</th>
              <th className="px-5 py-3">Referência</th>
              <th className="px-5 py-3">Interpretação</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {parametros.map((p) => {
              const interp = p.interpretacao || "NORMAL";
              const colorClass = INTERPRETACAO_COLORS[interp] ?? INTERPRETACAO_COLORS.NORMAL;
              return (
                <tr key={p.id ?? p.nome} className="transition hover:bg-slate-50/50">
                  <td className="px-5 py-3.5 font-medium text-slate-900">{p.nome}</td>
                  <td className="px-5 py-3.5">
                    <span className="font-semibold text-slate-800">{p.valor}</span>
                    {p.unidade && <span className="ml-1 text-slate-500">{p.unidade}</span>}
                  </td>
                  <td className="px-5 py-3.5 text-slate-600">
                    {p.valor_minimo && p.valor_maximo ? `${p.valor_minimo} – ${p.valor_maximo}` : "—"}
                  </td>
                  <td className="px-5 py-3.5">
                    <span className={`inline-flex rounded-lg border px-2.5 py-1 text-xs font-semibold ${colorClass}`}>
                      {INTERPRETACAO_LABELS[interp] ?? interp}
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
