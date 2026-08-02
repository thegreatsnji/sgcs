import { memo } from "react";
import { Link } from "react-router-dom";

import { Avatar, Button, EmptyState } from "@/design-system";
import { PRIORITY_LABELS } from "@/constants/appointments";
import { LabWorkflowProgress } from "@/features/laboratory/components/LabWorkflowProgress";
import { StatusBadge } from "@/features/laboratory/components/StatusBadge";
import type { LaboratoryOrder } from "@/types/laboratory";
import { formatDisplayDateTime } from "@/utils/date";

interface LaboratoryTableProps {
  orders: LaboratoryOrder[];
  onReceive?: (order: LaboratoryOrder) => void;
  onCollect?: (order: LaboratoryOrder) => void;
  onStart?: (order: LaboratoryOrder) => void;
  onFinish?: (order: LaboratoryOrder) => void;
  emptyTitle?: string;
  emptyDescription?: string;
}

function LaboratoryTableComponent({
  orders,
  onReceive,
  onCollect,
  onStart,
  onFinish,
  emptyTitle = "Sem pedidos",
  emptyDescription = "Não existem pedidos laboratoriais com os critérios actuais.",
}: LaboratoryTableProps) {
  if (orders.length === 0) {
    return <EmptyState title={emptyTitle} description={emptyDescription} />;
  }

  return (
    <div className="overflow-hidden rounded-2xl border border-slate-200/80 bg-white shadow-sm">
      <div className="overflow-x-auto">
        <table className="min-w-full text-sm">
          <thead className="sticky top-0 border-b border-slate-200 bg-slate-50/95 backdrop-blur-sm">
            <tr>
              {["Paciente", "Exame(s)", "Prioridade", "Estado", "Fluxo", "Data", ""].map((h) => (
                <th
                  key={h || "actions"}
                  scope="col"
                  className="px-4 py-3.5 text-left text-xs font-semibold tracking-wide text-slate-500 uppercase first:pl-6 last:pr-6"
                >
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {orders.map((row) => (
              <tr key={row.id} className="transition hover:bg-slate-50/80">
                <td className="px-4 py-4 pl-6">
                  <Link to={`/laboratory/${row.id}`} className="flex items-center gap-3 focus-ring rounded-lg">
                    <Avatar name={row.paciente.full_name} size="sm" />
                    <div>
                      <p className="font-medium text-slate-900 hover:text-primary-600">{row.paciente.full_name}</p>
                      <p className="font-mono text-xs text-slate-500">{row.numero_pedido}</p>
                    </div>
                  </Link>
                </td>
                <td className="max-w-[180px] px-4 py-4 text-slate-700">
                  <p className="line-clamp-2">{row.exames.map((e) => e.nome_exame).join(", ") || "—"}</p>
                </td>
                <td className="px-4 py-4 text-slate-700">
                  {PRIORITY_LABELS[row.prioridade as keyof typeof PRIORITY_LABELS] ?? row.prioridade}
                </td>
                <td className="px-4 py-4">
                  <StatusBadge status={row.estado} />
                </td>
                <td className="min-w-[120px] px-4 py-4">
                  <LabWorkflowProgress status={row.estado} compact />
                </td>
                <td className="px-4 py-4 text-slate-500">{formatDisplayDateTime(row.data_pedido)}</td>
                <td className="px-4 py-4 pr-6">
                  <div className="flex flex-wrap justify-end gap-1.5">
                    <Link to={`/laboratory/${row.id}`}>
                      <Button size="sm" variant="outline">
                        Ver
                      </Button>
                    </Link>
                    {row.estado === "PENDENTE" && onReceive && (
                      <Button size="sm" variant="primary" onClick={() => onReceive(row)}>
                        Receber
                      </Button>
                    )}
                    {(row.estado === "RECEBIDO" || row.estado === "AGUARDANDO_COLHEITA") && onCollect && (
                      <Button size="sm" variant="secondary" onClick={() => onCollect(row)}>
                        Colheita
                      </Button>
                    )}
                    {(row.estado === "RECEBIDO" || row.estado === "AGUARDANDO_COLHEITA") && onStart && (
                      <Button size="sm" variant="secondary" onClick={() => onStart(row)}>
                        Processar
                      </Button>
                    )}
                    {row.estado === "EM_PROCESSAMENTO" && onFinish && (
                      <Button size="sm" variant="primary" onClick={() => onFinish(row)}>
                        Concluir
                      </Button>
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

export const LaboratoryTable = memo(LaboratoryTableComponent);
