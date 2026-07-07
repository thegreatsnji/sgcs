import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link } from "react-router-dom";

import { Button, Card, ErrorState, LoadingState, Table, useToast } from "@/design-system";
import { BillingSubNav } from "@/features/billing/components/BillingSubNav";
import { billingService } from "@/services/billing/billing.service";
import type { BillingService as BillingServiceType } from "@/types/billing";
import { getApiErrorMessage } from "@/utils/api-error";

export function ServicesListPage() {
  const { showToast } = useToast();
  const queryClient = useQueryClient();
  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["billing-services"],
    queryFn: () => billingService.listServices(),
  });

  const toggleMutation = useMutation({
    mutationFn: ({ id, activo }: { id: number; activo: boolean }) =>
      billingService.updateService(id, { activo }),
    onSuccess: () => {
      showToast("Serviço actualizado.", "success");
      void queryClient.invalidateQueries({ queryKey: ["billing-services"] });
    },
    onError: (e) => showToast(getApiErrorMessage(e), "error"),
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between gap-4">
        <h2 className="text-2xl font-bold text-slate-900">Serviços</h2>
        <Link to="/billing/services/new"><Button variant="primary">Novo serviço</Button></Link>
      </div>
      <BillingSubNav />
      {isLoading || !data ? <LoadingState /> : isError ? (
        <ErrorState onRetry={() => void refetch()} message="Erro ao carregar serviços." />
      ) : (
        <Card>
          <Table<BillingServiceType>
            data={data.results}
            getRowKey={(r) => r.id}
            columns={[
              { key: "codigo", header: "Código" },
              { key: "nome", header: "Nome" },
              { key: "categoria", header: "Categoria" },
              { key: "preco", header: "Preço", render: (r) => `${r.preco} FCFA` },
              {
                key: "activo",
                header: "Estado",
                render: (r) => (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => toggleMutation.mutate({ id: r.id, activo: !r.activo })}
                  >
                    {r.activo ? "Activo" : "Inactivo"}
                  </Button>
                ),
              },
            ]}
          />
        </Card>
      )}
    </div>
  );
}
