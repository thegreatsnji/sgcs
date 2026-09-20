import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link } from "react-router-dom";

import { Button, Card, LoadingState, useToast } from "@/design-system";
import { BillingSubNav } from "@/features/billing/components/BillingSubNav";
import { billingService } from "@/services/billing/billing.service";
import { getApiErrorMessage } from "@/utils/api-error";

export function PendingReductionsPage() {
  const { showToast } = useToast();
  const qc = useQueryClient();
  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["billing-reducoes-pendentes"],
    queryFn: () => billingService.listReductionAuths({ estado: "PENDENTE" }),
  });

  const decide = useMutation({
    mutationFn: ({ id, aprovar }: { id: number; aprovar: boolean }) =>
      aprovar ? billingService.approveReduction(id) : billingService.rejectReduction(id),
    onSuccess: () => {
      showToast("Decisão registada.", "success");
      void qc.invalidateQueries({ queryKey: ["billing-reducoes-pendentes"] });
    },
    onError: (e) => showToast(getApiErrorMessage(e), "error"),
  });

  if (isLoading) return <LoadingState />;
  if (isError) {
    return (
      <div className="space-y-4">
        <h2 className="text-2xl font-bold">Reduções pendentes</h2>
        <BillingSubNav />
        <p className="text-sm text-red-700">Não foi possível carregar os pedidos.</p>
        <Button type="button" onClick={() => void refetch()}>
          Tentar novamente
        </Button>
      </div>
    );
  }

  const rows = data?.results ?? [];

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Reduções pendentes</h2>
      <BillingSubNav />
      <Card title="Autorização de valor especial">
        {rows.length === 0 ? (
          <p className="text-sm text-slate-600">Não há pedidos pendentes.</p>
        ) : (
          <ul className="divide-y">
            {rows.map((r) => (
              <li key={r.id} className="flex flex-wrap items-start justify-between gap-4 py-4 text-sm">
                <div>
                  <p className="font-medium">{r.servico_nome}</p>
                  <p className="text-slate-600">
                    Preço oficial: {Number(r.preco_oficial).toLocaleString("pt-PT")} FCFA. Valor
                    proposto: {Number(r.preco_proposto).toLocaleString("pt-PT")} FCFA (
                    {Number(r.percentual_reducao).toFixed(0)}%)
                  </p>
                  <p className="text-slate-600">Motivo: {r.motivo_reducao}</p>
                  {r.paciente_nome ? (
                    <p className="text-slate-600">Paciente: {r.paciente_nome}</p>
                  ) : null}
                  <p className="text-xs text-slate-500">
                    Solicitado por {r.solicitado_por_nome ?? "—"}
                  </p>
                </div>
                <div className="flex gap-2">
                  {r.fatura ? (
                    <Link
                      to={`/billing/invoices/${r.fatura}`}
                      className="rounded-xl border border-border px-4 py-2 text-sm hover:bg-slate-50"
                    >
                      Ver fatura
                    </Link>
                  ) : null}
                  <Button
                    type="button"
                    variant="primary"
                    disabled={decide.isPending}
                    onClick={() => decide.mutate({ id: r.id, aprovar: true })}
                  >
                    Aprovar
                  </Button>
                  <Button
                    type="button"
                    variant="secondary"
                    disabled={decide.isPending}
                    onClick={() => decide.mutate({ id: r.id, aprovar: false })}
                  >
                    Rejeitar
                  </Button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </Card>
    </div>
  );
}
