import { memo } from "react";
import { Link } from "react-router-dom";

import { Avatar, Button, EmptyState } from "@/design-system";
import type { LaboratoryResult } from "@/types/laboratoryResult";
import { formatDisplayDateTime } from "@/utils/date";
import { ResultadoStatusBadge } from "./ResultadoStatusBadge";

interface TabelaResultadosProps {
  resultados: LaboratoryResult[];
  emptyMessage?: string;
}

function TabelaResultadosComponent({
  resultados,
  emptyMessage = "Sem resultados.",
}: TabelaResultadosProps) {
  if (resultados.length === 0) {
    return (
      <EmptyState
        title="Sem resultados"
        description={emptyMessage}
      />
    );
  }

  return (
    <div className="overflow-hidden rounded-2xl border border-slate-200/80">
      <div className="overflow-x-auto">
        <table className="min-w-full text-sm">
          <thead className="sticky top-0 border-b border-slate-200 bg-slate-50/95 backdrop-blur-sm">
            <tr>
              {["Pedido", "Paciente", "Estado", "Data", "Responsável", "Acções"].map((h) => (
                <th
                  key={h}
                  scope="col"
                  className="px-4 py-3.5 text-left text-xs font-semibold tracking-wide text-slate-500 uppercase first:pl-6"
                >
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 bg-white">
            {resultados.map((row) => (
              <tr key={row.id} className="transition hover:bg-slate-50/80">
                <td className="px-4 py-3.5 pl-6">
                  <Link
                    to={`/laboratory/results/${row.id}`}
                    className="font-mono text-sm font-medium text-primary-600 hover:text-primary-700"
                  >
                    {row.numero_pedido}
                  </Link>
                </td>
                <td className="px-4 py-3.5">
                  <div className="flex items-center gap-2">
                    <Avatar name={row.paciente_nome} size="sm" />
                    <span className="font-medium text-slate-900">{row.paciente_nome}</span>
                  </div>
                </td>
                <td className="px-4 py-3.5">
                  <ResultadoStatusBadge status={row.estado} />
                </td>
                <td className="px-4 py-3.5 text-slate-500">
                  {row.data_resultado ? formatDisplayDateTime(row.data_resultado) : "—"}
                </td>
                <td className="px-4 py-3.5 text-slate-600">{row.responsavel_nome ?? "—"}</td>
                <td className="px-4 py-3.5">
                  <div className="flex flex-wrap gap-1.5">
                    {row.editavel && (
                      <Link to={`/laboratory/results/${row.id}/edit`}>
                        <Button variant="ghost" className="!px-2 !py-1 text-xs">
                          Editar
                        </Button>
                      </Link>
                    )}
                    <Link to={`/laboratory/results/${row.id}`}>
                      <Button variant="outline" className="!px-2 !py-1 text-xs">
                        {row.estado === "RESULTADO_PENDENTE" ? "Validar" : "Abrir"}
                      </Button>
                    </Link>
                    {(row.estado === "VALIDADO" || row.estado === "ENTREGUE") && (
                      <Link to={`/laboratory/results/${row.id}`}>
                        <Button variant="ghost" className="!px-2 !py-1 text-xs">
                          Imprimir
                        </Button>
                      </Link>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export const TabelaResultados = memo(TabelaResultadosComponent);
