import { Link } from "react-router-dom";

import { Button, Card, Table } from "@/design-system";
import { ResultadoStatusBadge } from "@/features/laboratory/results/components/ResultadoStatusBadge";
import { laboratoryResultsService } from "@/services/laboratory";
import type { ClinicalLaboratoryResult } from "@/types/laboratoryResult";
import { formatDisplayDateTime } from "@/utils/date";

interface ResultadosLaboratorioTabProps {
  resultados: ClinicalLaboratoryResult[];
}

export function ResultadosLaboratorioTab({ resultados }: ResultadosLaboratorioTabProps) {
  if (!resultados.length) {
    return (
      <Card title="Resultados laboratoriais">
        <p className="text-sm text-slate-500">Ainda não existem resultados validados para esta consulta.</p>
      </Card>
    );
  }

  return (
    <Card title="Resultados laboratoriais">
      <Table<ClinicalLaboratoryResult>
        data={resultados}
        getRowKey={(row) => row.id}
        emptyMessage="Sem resultados."
        columns={[
          { key: "numero_pedido", header: "Pedido" },
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
          { key: "responsavel", header: "Responsável", render: (row) => row.responsavel ?? "—" },
          {
            key: "actions",
            header: "Acções",
            render: (row) => (
              <div className="flex flex-wrap gap-2">
                <Link to={`/laboratory/results/${row.id}`}>
                  <Button variant="ghost" size="sm">
                    Visualizar
                  </Button>
                </Link>
                {row.anexos[0] && (
                  <a
                    href={laboratoryResultsService.downloadUrl(row.id, row.anexos[0].id)}
                    className="inline-flex items-center text-sm text-primary-700 hover:underline"
                    target="_blank"
                    rel="noreferrer"
                  >
                    Download
                  </a>
                )}
              </div>
            ),
          },
        ]}
      />
    </Card>
  );
}
