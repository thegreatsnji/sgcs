import { useQuery } from "@tanstack/react-query";
import { useState } from "react";

import { Card } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { Spinner } from "@/components/ui/Spinner";
import { Table } from "@/components/tables/Table";
import { auditService } from "@/services/audit";

export function AuditPage() {
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);

  const { data, isLoading } = useQuery({
    queryKey: ["audit-logs", page, search],
    queryFn: () => auditService.list({ page, search: search || undefined }),
  });

  if (isLoading) {
    return <Spinner label="A carregar auditoria..." />;
  }

  const logs = data?.results ?? [];

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900">Auditoria</h2>
        <p className="text-sm text-slate-500">Registo de ações importantes do sistema</p>
      </div>

      <Card>
        <div className="mb-4 max-w-md">
          <Input
            label="Pesquisar"
            placeholder="Descrição da ação"
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setPage(1);
            }}
          />
        </div>

        <Table
          columns={[
            { key: "created_at", header: "Data/Hora" },
            { key: "user_name", header: "Utilizador" },
            { key: "action", header: "Ação" },
            { key: "description", header: "Descrição" },
            { key: "ip_address", header: "IP" },
          ]}
          data={logs}
        />
      </Card>
    </div>
  );
}
