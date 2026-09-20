import { memo } from "react";
import { Link } from "react-router-dom";

import { Avatar, Button } from "@/design-system";
import { PRIORITY_LABELS } from "@/constants/appointments";
import { StatusBadge } from "@/features/laboratory/components/StatusBadge";
import { LabWorkflowProgress } from "@/features/laboratory/components/LabWorkflowProgress";
import type { LaboratoryOrder } from "@/types/laboratory";
import { formatDisplayDateTime } from "@/utils/date";

interface CollectionPatientCardProps {
  order: LaboratoryOrder;
  onCollect?: (order: LaboratoryOrder) => void;
}

const PRIORITY_VARIANT: Record<string, string> = {
  EMERGENCY: "border-red-300 bg-red-50/50",
  HIGH: "border-amber-300 bg-amber-50/50",
  NORMAL: "border-slate-200/80 bg-white",
  LOW: "border-slate-200/80 bg-white",
};

function CollectionPatientCardComponent({ order, onCollect }: CollectionPatientCardProps) {
  const examNames = order.exames.map((e) => e.nome_exame).join(", ") || "—";
  const priorityClass = PRIORITY_VARIANT[order.prioridade] ?? PRIORITY_VARIANT.NORMAL;

  return (
    <article
      className={`rounded-2xl border p-5 shadow-sm transition hover:shadow-md ${priorityClass}`}
    >
      <div className="flex items-start gap-4">
        <Avatar name={order.paciente.full_name} size="md" />
        <div className="min-w-0 flex-1">
          <div className="flex items-start justify-between gap-2">
            <div>
              <Link
                to={`/laboratory/${order.id}`}
                className="font-semibold text-slate-900 hover:text-primary-600"
              >
                {order.paciente.full_name}
              </Link>
              <p className="text-xs text-slate-500">{order.paciente.patient_number}</p>
            </div>
            <StatusBadge status={order.estado} />
          </div>

          <dl className="mt-4 grid grid-cols-2 gap-3 text-xs">
            <div>
              <dt className="font-semibold tracking-wide text-slate-400 uppercase">Exame</dt>
              <dd className="mt-0.5 font-medium text-slate-800">{examNames}</dd>
            </div>
            <div>
              <dt className="font-semibold tracking-wide text-slate-400 uppercase">Prioridade</dt>
              <dd className="mt-0.5 font-medium text-slate-800">
                {PRIORITY_LABELS[order.prioridade as keyof typeof PRIORITY_LABELS] ?? order.prioridade}
              </dd>
            </div>
            <div>
              <dt className="font-semibold tracking-wide text-slate-400 uppercase">Pedido</dt>
              <dd className="mt-0.5 font-mono text-slate-600">{order.numero_pedido}</dd>
            </div>
            <div>
              <dt className="font-semibold tracking-wide text-slate-400 uppercase">Agendado</dt>
              <dd className="mt-0.5 text-slate-600">{formatDisplayDateTime(order.data_pedido)}</dd>
            </div>
          </dl>

          <div className="mt-4">
            <p className="mb-2 text-[10px] font-semibold tracking-wide text-slate-400 uppercase">
              Estado da colheita
            </p>
            <LabWorkflowProgress status={order.estado} compact />
          </div>
        </div>
      </div>

      <div className="mt-4 flex flex-wrap gap-2 border-t border-slate-100 pt-4">
        <Link to={`/laboratory/${order.id}`}>
          <Button size="sm" variant="outline">
            Detalhes
          </Button>
        </Link>
        {order.estado === "RECEBIDO" && onCollect && (
          <Button size="sm" variant="primary" onClick={() => onCollect(order)}>
            Registar colheita
          </Button>
        )}
        {order.estado === "AGUARDANDO_COLHEITA" && (
          <Link to={`/laboratory/${order.id}`}>
            <Button size="sm" variant="primary">
              Continuar processamento
            </Button>
          </Link>
        )}
      </div>
    </article>
  );
}

export const CollectionPatientCard = memo(CollectionPatientCardComponent);
