import { Link } from "react-router-dom";
import { Badge, Table } from "@/design-system";
import type { CashRegister } from "@/types/finance";

export function CashRegisterTable({ registers }: { registers: CashRegister[] }) {
  return (
    <Table<CashRegister>
      data={registers}
      getRowKey={(r) => r.id}
      emptyMessage="Sem caixas."
      columns={[
        {
          key: "codigo",
          header: "Código",
          render: (r) => <Link to={`/finance/cash/${r.id}`} className="text-primary-700">{r.codigo}</Link>,
        },
        { key: "nome", header: "Nome" },
        { key: "estado", header: "Estado", render: (r) => <Badge>{r.estado}</Badge> },
        { key: "saldo_actual", header: "Saldo", render: (r) => `${r.saldo_actual} FCFA` },
      ]}
    />
  );
}
