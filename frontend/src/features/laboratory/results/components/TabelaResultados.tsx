import { Link } from "react-router-dom";

import { Table } from "@/design-system";
import type { LaboratoryResult } from "@/types/laboratoryResult";
import { formatDisplayDateTime } from "@/utils/date";
import { ResultadoStatusBadge } from "./ResultadoStatusBadge";

interface TabelaResultadosProps {
  resultados: LaboratoryResult[];
  emptyMessage?: string;
}

export function TabelaResultados({
  resultados,
  emptyMessage = "Sem resultados.",
}: TabelaResultadosProps) {
  return (
    <Table<LaboratoryResult>
      data={resultados}
      getRowKey={(row) => row.id}
      emptyMessage={emptyMessage}
      columns={[
        {
          key: "numero_pedido",
          header: "Pedido",
          render: (row) => (
            <Link to={`/laboratory/results/${row.id}`} className="font-medium text-primary-700 hover:underline">
              {row.numero_pedido}
            </Link>
          ),
        },
        { key: "paciente_nome", header: "Paciente" },
        {
          key: "estado",
          header: "Estado",
          render: (row) => <ResultadoStatusBadge status={row.estado} />,
        },
        {
          key: "data_resultado",
          header: "Data",
          render: (row) =>
            row.data_resultado ? formatDisplayDateTime(row.data_resultado) : "—",
        },
        { key: "responsavel_nome", header: "Responsável", render: (row) => row.responsavel_nome ?? "—" },
      ]}
    />
  );
}
