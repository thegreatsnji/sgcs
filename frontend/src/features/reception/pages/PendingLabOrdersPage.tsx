import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { useState } from "react";

import { Badge, Button, Card, EmptyState, ErrorState, LoadingState, useToast } from "@/design-system";
import { BillingSubNav } from "@/features/billing/components/BillingSubNav";
import { UI_COPY } from "@/constants/uiCopy";
import { receptionService } from "@/services/reception";
import { getApiErrorMessage } from "@/utils/api-error";
import { formatDisplayDateTime } from "@/utils/date";

type FaturacaoFilter = "AGUARDA_REGULARIZACAO" | "REGULARIZADO" | "TODOS";

export function PendingLabOrdersPage() {
  const { showToast } = useToast();
  const queryClient = useQueryClient();
  const [filtro, setFiltro] = useState<FaturacaoFilter>("AGUARDA_REGULARIZACAO");

  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["pending-clinical-lab-orders", filtro],
    queryFn: () =>
      receptionService.getPendingClinicalLabOrders({ estado_faturacao: filtro }),
  });

  const markMutation = useMutation({
    mutationFn: (id: number) => receptionService.markLabOrderBilled(id),
    onSuccess: (result) => {
      showToast(
        result.already_regularized
          ? "Pedido já estava regularizado."
          : "Pedido marcado como regularizado.",
        "success",
      );
      void queryClient.invalidateQueries({ queryKey: ["pending-clinical-lab-orders"] });
    },
    onError: (e) => showToast(getApiErrorMessage(e), "error"),
  });

  const rows = data ?? [];
  const retornoLab = encodeURIComponent("/reception/lab-orders");

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-900">
          {UI_COPY.nav.labOrdersToSettle}
        </h1>
        <p className="mt-1 text-slate-500">
          Retorno só para pagar exames — <strong className="font-semibold text-slate-700">sem triagem</strong>.
          Cobrar no fluxo de faturação; após o pagamento o pedido fica regularizado e o laboratório
          pode processar.
        </p>
      </div>

      <BillingSubNav />

      <div className="flex flex-wrap gap-2">
        {(
          [
            ["AGUARDA_REGULARIZACAO", "Aguardam regularização"],
            ["REGULARIZADO", "Regularizados"],
            ["TODOS", "Todos"],
          ] as const
        ).map(([value, label]) => (
          <Button
            key={value}
            size="sm"
            variant={filtro === value ? "primary" : "outline"}
            onClick={() => setFiltro(value)}
          >
            {label}
          </Button>
        ))}
      </div>

      {isLoading ? (
        <LoadingState message="A carregar pedidos..." />
      ) : isError ? (
        <ErrorState message="Erro ao carregar pedidos." onRetry={() => void refetch()} />
      ) : rows.length === 0 ? (
        <EmptyState
          title="Sem pedidos"
          description="Não existem pedidos laboratoriais com este filtro."
        />
      ) : (
        <Card>
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead className="border-b border-slate-200 bg-slate-50">
                <tr>
                  {["Utente", "Exame", "Serviço", "Estado", "Pedido em", ""].map((h) => (
                    <th
                      key={h || "a"}
                      className="px-4 py-3 text-left text-xs font-semibold tracking-wide text-slate-500 uppercase"
                    >
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {rows.map((row) => {
                  const invoiceUrl =
                    `/billing/invoices/new?paciente=${row.paciente_id}` +
                    `&pedido_lab=${row.id}` +
                    `&retorno=${retornoLab}` +
                    (row.servico?.id ? `&servico=${row.servico.id}` : "");
                  return (
                    <tr key={row.id}>
                      <td className="px-4 py-3">
                        <p className="font-medium text-slate-900">{row.paciente_nome}</p>
                        <p className="font-mono text-xs text-slate-500">{row.paciente_codigo}</p>
                      </td>
                      <td className="px-4 py-3 text-slate-700">{row.tipo_exame}</td>
                      <td className="px-4 py-3 text-slate-600">
                        {row.servico ? row.servico.nome : "—"}
                      </td>
                      <td className="px-4 py-3">
                        <Badge
                          variant={
                            row.estado_faturacao === "REGULARIZADO" ? "success" : "warning"
                          }
                        >
                          {row.estado_faturacao_label}
                        </Badge>
                      </td>
                      <td className="px-4 py-3 text-slate-500">
                        {formatDisplayDateTime(row.created_at)}
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex flex-wrap justify-end gap-2">
                          {row.estado_faturacao !== "REGULARIZADO" ? (
                            <Link to={invoiceUrl}>
                              <Button size="sm" variant="primary">
                                Cobrar exame
                              </Button>
                            </Link>
                          ) : null}
                          {row.estado_faturacao !== "REGULARIZADO" ? (
                            <Button
                              size="sm"
                              variant="outline"
                              isLoading={markMutation.isPending}
                              onClick={() => {
                                if (
                                  window.confirm(
                                    "Marcar este exame como regularizado sem novo pagamento?\n\nUse só se a cobrança já foi tratada noutro recibo. Isto não cria um pagamento.",
                                  )
                                ) {
                                  markMutation.mutate(row.id);
                                }
                              }}
                            >
                              Já cobrado
                            </Button>
                          ) : null}
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </Card>
      )}
    </div>
  );
}
