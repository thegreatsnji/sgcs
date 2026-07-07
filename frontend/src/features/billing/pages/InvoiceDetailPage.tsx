import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useParams } from "react-router-dom";

import { Button, Card, LoadingState, useToast } from "@/design-system";
import { BillingSubNav } from "@/features/billing/components/BillingSubNav";
import { PaymentForm } from "@/features/billing/components/PaymentForm";
import { billingService } from "@/services/billing/billing.service";
import { getApiErrorMessage } from "@/utils/api-error";
import { formatDisplayDateTime } from "@/utils/date";

export function InvoiceDetailPage() {
  const { id } = useParams<{ id: string }>();
  const invoiceId = Number(id);
  const { showToast } = useToast();
  const queryClient = useQueryClient();
  const { data, isLoading } = useQuery({
    queryKey: ["billing-invoice", invoiceId],
    queryFn: () => billingService.getInvoice(invoiceId),
    enabled: Number.isFinite(invoiceId),
  });

  const payMutation = useMutation({
    mutationFn: billingService.createPayment,
    onSuccess: () => {
      showToast("Pagamento registado.", "success");
      void queryClient.invalidateQueries({ queryKey: ["billing-invoice", invoiceId] });
    },
    onError: (e) => showToast(getApiErrorMessage(e), "error"),
  });

  const confirmMutation = useMutation({
    mutationFn: billingService.confirmPayment,
    onSuccess: () => {
      showToast("Pagamento confirmado.", "success");
      void queryClient.invalidateQueries({ queryKey: ["billing-invoice", invoiceId] });
    },
    onError: (e) => showToast(getApiErrorMessage(e), "error"),
  });

  if (isLoading || !data) return <LoadingState />;

  const pendente = data.total_pago && Number(data.total_pago) < Number(data.total)
    ? String(Number(data.total) - Number(data.total_pago))
    : data.total;

  return (
    <div className="space-y-6">
      <div className="flex justify-between">
        <div>
          <h2 className="text-2xl font-bold">{data.numero}</h2>
          <p className="text-slate-600">{data.paciente_nome}</p>
        </div>
        <span className="text-sm font-medium">{data.estado}</span>
      </div>
      <BillingSubNav />
      <Card title="Resumo">
        <dl className="grid gap-2 text-sm sm:grid-cols-2">
          <div><dt className="text-slate-500">Total</dt><dd>{data.total} FCFA</dd></div>
          <div><dt className="text-slate-500">Pago</dt><dd>{data.total_pago} FCFA</dd></div>
          <div><dt className="text-slate-500">Emitida</dt><dd>{data.emitida_em ? formatDisplayDateTime(data.emitida_em) : "—"}</dd></div>
        </dl>
        <ul className="mt-4 space-y-1 text-sm">
          {data.itens.map((i) => (
            <li key={i.id}>{i.servico_nome} × {i.quantidade} — {i.subtotal} FCFA</li>
          ))}
        </ul>
      </Card>
      {data.editavel && (
        <Card title="Registar pagamento">
          <PaymentForm faturaId={invoiceId} valorSugerido={pendente} onSubmit={(v) => payMutation.mutate(v)} isPending={payMutation.isPending} />
        </Card>
      )}
      {data.pagamentos.length > 0 && (
        <Card title="Pagamentos">
          <ul className="space-y-2 text-sm">
            {data.pagamentos.map((p) => (
              <li key={p.id} className="flex items-center justify-between gap-2">
                <span>{p.valor} FCFA — {p.estado}</span>
                {p.estado === "PENDENTE" && (
                  <Button size="sm" onClick={() => confirmMutation.mutate(p.id)} disabled={confirmMutation.isPending}>
                    Confirmar
                  </Button>
                )}
              </li>
            ))}
          </ul>
        </Card>
      )}
    </div>
  );
}
