import { memo } from "react";
import { Link } from "react-router-dom";

import { Avatar, Button } from "@/design-system";
import { PRIORITY_LABELS } from "@/constants/appointments";
import { LabWorkflowProgress } from "@/features/laboratory/components/LabWorkflowProgress";
import { StatusBadge } from "@/features/laboratory/components/StatusBadge";
import type { LaboratoryOrder } from "@/types/laboratory";
import { formatDisplayDateTime } from "@/utils/date";

interface LaboratoryCardProps {
  order: LaboratoryOrder;
  onReceive?: (order: LaboratoryOrder) => void;
}

function LaboratoryCardComponent({ order, onReceive }: LaboratoryCardProps) {
  const examName = order.exames[0]?.nome_exame ?? "—";

  return (
    <article className="rounded-2xl border border-slate-200/80 bg-white p-5 shadow-sm transition hover:border-primary-200 hover:shadow-md">
      <div className="flex items-start gap-3">
        <Avatar name={order.paciente.full_name} size="sm" />
        <div className="min-w-0 flex-1">
          <div className="flex items-start justify-between gap-2">
            <div>
              <Link
                to={`/laboratory/${order.id}`}
                className="font-semibold text-slate-900 hover:text-primary-600"
              >
                {order.numero_pedido}
              </Link>
              <p className="text-sm text-slate-700">{order.paciente.full_name}</p>
              <p className="text-xs text-slate-500">{examName}</p>
            </div>
            <StatusBadge status={order.estado} />
          </div>
          <p className="mt-2 text-xs text-slate-400">
            {PRIORITY_LABELS[order.prioridade as keyof typeof PRIORITY_LABELS] ?? order.prioridade} ·{" "}
            {formatDisplayDateTime(order.data_pedido)}
          </p>
          <div className="mt-3">
            <LabWorkflowProgress status={order.estado} compact />
          </div>
        </div>
      </div>
      {order.estado === "PENDENTE" && onReceive && (
        <div className="mt-4 border-t border-slate-100 pt-3">
          <Button size="sm" variant="primary" onClick={() => onReceive(order)}>
            Receber pedido
          </Button>
        </div>
      )}
    </article>
  );
}

export const LaboratoryCard = memo(LaboratoryCardComponent);
