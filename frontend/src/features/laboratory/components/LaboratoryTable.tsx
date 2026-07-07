import { Link } from "react-router-dom";

import { Button, Table } from "@/design-system";
import { PRIORITY_LABELS } from "@/constants/appointments";
import { StatusBadge } from "@/features/laboratory/components/StatusBadge";
import type { LaboratoryOrder } from "@/types/laboratory";
import { formatDisplayDateTime } from "@/utils/date";

interface LaboratoryTableProps {
  orders: LaboratoryOrder[];
  onReceive?: (order: LaboratoryOrder) => void;
  onCollect?: (order: LaboratoryOrder) => void;
  onStart?: (order: LaboratoryOrder) => void;
  onFinish?: (order: LaboratoryOrder) => void;
}

export function LaboratoryTable({
  orders,
  onReceive,
  onCollect,
  onStart,
  onFinish,
}: LaboratoryTableProps) {
  return (
    <Table<LaboratoryOrder>
      data={orders}
      getRowKey={(row) => row.id}
      emptyMessage="Sem pedidos laboratoriais."
      columns={[
        { key: "numero_pedido", header: "N.º pedido" },
        {
          key: "paciente",
          header: "Paciente",
          render: (row) => (
            <div>
              <p className="font-medium">{row.paciente.full_name}</p>
              <p className="text-xs text-slate-500">{row.paciente.patient_number}</p>
            </div>
          ),
        },
        {
          key: "exames",
          header: "Exame(s)",
          render: (row) => row.exames.map((e) => e.nome_exame).join(", ") || "—",
        },
        {
          key: "prioridade",
          header: "Prioridade",
          render: (row) =>
            PRIORITY_LABELS[row.prioridade as keyof typeof PRIORITY_LABELS] ?? row.prioridade,
        },
        {
          key: "estado",
          header: "Estado",
          render: (row) => <StatusBadge status={row.estado} />,
        },
        {
          key: "data_pedido",
          header: "Data",
          render: (row) => formatDisplayDateTime(row.data_pedido),
        },
        {
          key: "actions",
          header: "Acções",
          render: (row) => (
            <div className="flex flex-wrap gap-2">
              <Link to={`/laboratory/${row.id}`}>
                <Button size="sm" variant="outline">Detalhe</Button>
              </Link>
              {row.estado === "PENDENTE" && onReceive && (
                <Button size="sm" variant="primary" onClick={() => onReceive(row)}>Receber</Button>
              )}
              {(row.estado === "RECEBIDO" || row.estado === "AGUARDANDO_COLHEITA") && onCollect && (
                <Button size="sm" variant="secondary" onClick={() => onCollect(row)}>Colheita</Button>
              )}
              {(row.estado === "RECEBIDO" || row.estado === "AGUARDANDO_COLHEITA") && onStart && (
                <Button size="sm" variant="secondary" onClick={() => onStart(row)}>Processar</Button>
              )}
              {row.estado === "EM_PROCESSAMENTO" && onFinish && (
                <Button size="sm" variant="primary" onClick={() => onFinish(row)}>Concluir</Button>
              )}
            </div>
          ),
        },
      ]}
    />
  );
}
