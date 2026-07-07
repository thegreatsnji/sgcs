import { Table } from "@/design-system";
import type { FinanceMovement } from "@/types/finance";
import { formatDisplayDateTime } from "@/utils/date";

export function CashMovementTable({ movements }: { movements: FinanceMovement[] }) {
  return (
    <Table<FinanceMovement>
      data={movements}
      getRowKey={(m) => m.id}
      columns={[
        { key: "data", header: "Data", render: (m) => formatDisplayDateTime(m.data) },
        { key: "tipo", header: "Tipo" },
        { key: "origem", header: "Origem" },
        { key: "descricao", header: "Descrição" },
        { key: "valor", header: "Valor", render: (m) => `${m.valor} FCFA` },
      ]}
    />
  );
}
