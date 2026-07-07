import { Link } from "react-router-dom";

import { Card } from "@/design-system";
import { StatusBadge } from "@/features/laboratory/components/StatusBadge";
import type { LaboratoryOrder } from "@/types/laboratory";
import { formatDisplayDateTime } from "@/utils/date";

interface LaboratoryCardProps {
  order: LaboratoryOrder;
}

export function LaboratoryCard({ order }: LaboratoryCardProps) {
  return (
    <Card>
      <div className="flex items-start justify-between gap-3">
        <div>
          <Link to={`/laboratory/${order.id}`} className="font-semibold text-primary-700 hover:underline">
            {order.numero_pedido}
          </Link>
          <p className="text-sm text-slate-600">{order.paciente.full_name}</p>
          <p className="text-xs text-slate-500">{order.exames[0]?.nome_exame ?? "—"}</p>
        </div>
        <StatusBadge status={order.estado} />
      </div>
      <p className="mt-2 text-xs text-slate-400">{formatDisplayDateTime(order.data_pedido)}</p>
    </Card>
  );
}
