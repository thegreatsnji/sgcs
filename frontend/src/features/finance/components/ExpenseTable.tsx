import { Table, Badge } from "@/design-system";
import type { Expense } from "@/types/finance";

export function ExpenseTable({ expenses }: { expenses: Expense[] }) {
  return (
    <Table<Expense>
      data={expenses}
      getRowKey={(e) => e.id}
      columns={[
        { key: "fornecedor", header: "Fornecedor" },
        { key: "categoria", header: "Categoria" },
        { key: "valor", header: "Valor", render: (e) => `${e.valor} FCFA` },
        { key: "estado", header: "Estado", render: (e) => <Badge>{e.estado}</Badge> },
        { key: "data", header: "Data" },
      ]}
    />
  );
}
