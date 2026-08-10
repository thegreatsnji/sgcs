import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useRef } from "react";
import { Link, useNavigate, useParams, useSearchParams } from "react-router-dom";

import { Badge, Button, Card, useToast } from "@/design-system";
import { BillingSubNav } from "@/features/billing/components/BillingSubNav";
import { InvoiceDetailSkeleton } from "@/features/billing/components/BillingSkeleton";
import { InvoiceStatusBadge } from "@/features/billing/components/InvoiceStatusBadge";
import { PaymentForm } from "@/features/billing/components/PaymentForm";
import { ReceptionAtendimentoBanner } from "@/features/reception/components/ReceptionAtendimentoBanner";
import {
  METODO_PAGAMENTO_LABEL,
  PAGAMENTO_ESTADO_LABEL,
  formatCurrency,
} from "@/features/billing/utils/formatBilling";
import { billingService } from "@/services/billing/billing.service";
import { getApiErrorMessage } from "@/utils/api-error";
import { formatDisplayDateTime } from "@/utils/date";

export function InvoiceDetailPage() {
  const { id } = useParams<{ id: string }>();
  const invoiceId = Number(id);
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const pagarFocus = searchParams.get("pagar") === "1";
  const retorno = searchParams.get("retorno");
  const paymentSectionRef = useRef<HTMLDivElement>(null);
  const { showToast } = useToast();
  const queryClient = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ["billing-invoice", invoiceId],
    queryFn: () => billingService.getInvoice(invoiceId),
    enabled: Number.isFinite(invoiceId),
  });

  const { data: receiptsData } = useQuery({
    queryKey: ["billing-receipts"],
    queryFn: () => billingService.listReceipts({ page: 1, page_size: 50 }),
    enabled: Number.isFinite(invoiceId) && !!data,
  });

  const payMutation = useMutation({
    mutationFn: billingService.createPayment,
    onSuccess: () => {
      showToast("Pagamento registado.", "success");
      void queryClient.invalidateQueries({ queryKey: ["billing-invoice", invoiceId] });
      void queryClient.invalidateQueries({ queryKey: ["billing-receipts"] });
      void queryClient.invalidateQueries({ queryKey: ["billing-invoices", "payment-gate"] });
    },
    onError: (e) => showToast(getApiErrorMessage(e), "error"),
  });

  const confirmMutation = useMutation({
    mutationFn: billingService.confirmPayment,
    onSuccess: async (_payment, paymentId) => {
      showToast("Pagamento confirmado. Pode imprimir o recibo.", "success");
      void queryClient.invalidateQueries({ queryKey: ["billing-invoice", invoiceId] });
      void queryClient.invalidateQueries({ queryKey: ["billing-receipts"] });
      void queryClient.invalidateQueries({ queryKey: ["billing-invoices", "payment-gate"] });
      try {
        const receipts = await billingService.listReceipts({ page: 1, page_size: 100 });
        const recibo = receipts.results.find((r) => r.pagamento === paymentId);
        if (recibo) {
          const retornoQs = retorno ? `&retorno=${encodeURIComponent(retorno)}` : "";
          void navigate(`/billing/receipts/${recibo.id}?imprimir=1${retornoQs}`);
        }
      } catch {
        /* lista de recibos opcional para redireccionamento */
      }
    },
    onError: (e) => showToast(getApiErrorMessage(e), "error"),
  });

  useEffect(() => {
    if (!pagarFocus || isLoading || !data) return;
    paymentSectionRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
  }, [pagarFocus, isLoading, data]);

  if (isLoading || !data) return <InvoiceDetailSkeleton />;

  const total = Number(data.total);
  const totalPago = Number(data.total_pago);
  const pendente = totalPago < total ? total - totalPago : 0;
  const receipts = (receiptsData?.results ?? []).filter((r) => r.fatura_numero === data.numero);

  return (
    <div className="space-y-6">
      <ReceptionAtendimentoBanner retorno={retorno} />
      <div className="rounded-2xl border border-slate-200/80 bg-gradient-to-br from-white to-slate-50 p-6 shadow-sm">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
          <div className="space-y-2">
            <p className="text-xs font-semibold tracking-wide text-slate-500 uppercase">Fatura</p>
            <h1 className="text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">{data.numero}</h1>
            <p className="text-slate-600">
              Paciente:{" "}
              <Link to={`/patients/${data.paciente}`} className="font-medium text-primary-700 hover:underline">
                {data.paciente_nome}
              </Link>
            </p>
            {data.consulta_numero && (
              <p className="text-sm text-slate-500">Consulta: {data.consulta_numero}</p>
            )}
          </div>
          <div className="flex flex-col items-start gap-3 lg:items-end">
            <InvoiceStatusBadge estado={data.estado} />
            <div className="text-left lg:text-right">
              <p className="text-xs font-semibold tracking-wide text-slate-500 uppercase">Valor total</p>
              <p className="text-3xl font-bold text-slate-900">{formatCurrency(data.total)}</p>
              {pendente > 0 && (
                <p className="mt-1 text-sm text-amber-700">
                  Pendente: <span className="font-semibold">{formatCurrency(pendente)}</span>
                </p>
              )}
            </div>
          </div>
        </div>

        <dl className="mt-6 grid gap-4 border-t border-slate-200/80 pt-4 text-sm sm:grid-cols-2 lg:grid-cols-4">
          <div>
            <dt className="text-slate-500">Subtotal</dt>
            <dd className="font-medium text-slate-900">{formatCurrency(data.subtotal)}</dd>
          </div>
          <div>
            <dt className="text-slate-500">Desconto</dt>
            <dd className="font-medium text-slate-900">{formatCurrency(data.desconto)}</dd>
          </div>
          <div>
            <dt className="text-slate-500">Imposto</dt>
            <dd className="font-medium text-slate-900">{formatCurrency(data.imposto)}</dd>
          </div>
          <div>
            <dt className="text-slate-500">Total pago</dt>
            <dd className="font-medium text-green-700">{formatCurrency(data.total_pago)}</dd>
          </div>
          <div>
            <dt className="text-slate-500">Emitida em</dt>
            <dd className="font-medium text-slate-900">
              {data.emitida_em ? formatDisplayDateTime(data.emitida_em) : "—"}
            </dd>
          </div>
        </dl>
      </div>

      {!retorno ? <BillingSubNav /> : null}

      <Card title="Itens">
        {data.itens.length === 0 ? (
          <p className="text-sm text-slate-500">Sem itens na fatura.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-200 text-left text-xs font-semibold tracking-wide text-slate-500 uppercase">
                  <th className="pb-3 pr-4">Serviço</th>
                  <th className="pb-3 pr-4">Qtd.</th>
                  <th className="pb-3 pr-4">Preço unit.</th>
                  <th className="pb-3">Subtotal</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {data.itens.map((item) => (
                  <tr key={item.id}>
                    <td className="py-3 pr-4 font-medium text-slate-900">{item.servico_nome}</td>
                    <td className="py-3 pr-4 text-slate-600">{item.quantidade}</td>
                    <td className="py-3 pr-4 text-slate-600">
                      {formatCurrency(item.preco_unitario ?? item.preco ?? "0")}
                    </td>
                    <td className="py-3 font-medium text-slate-900">{formatCurrency(item.subtotal)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>

      {data.editavel && (
        <div ref={paymentSectionRef} id="registar-pagamento">
          <Card title="Registar pagamento">
            <PaymentForm
              faturaId={invoiceId}
              valorSugerido={pendente > 0 ? String(pendente) : data.total}
              onSubmit={(v) => payMutation.mutate(v)}
              isPending={payMutation.isPending}
            />
          </Card>
        </div>
      )}

      <Card title="Pagamentos">
        {data.pagamentos.length === 0 ? (
          <p className="text-sm text-slate-500">Nenhum pagamento registado.</p>
        ) : (
          <ul className="divide-y divide-slate-100">
            {data.pagamentos.map((payment) => (
              <li key={payment.id} className="flex flex-col gap-3 py-4 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <p className="font-semibold text-slate-900">{formatCurrency(payment.valor)}</p>
                  <p className="mt-1 text-sm text-slate-500">
                    {METODO_PAGAMENTO_LABEL[payment.metodo_pagamento]} ·{" "}
                    {payment.data_pagamento ? formatDisplayDateTime(payment.data_pagamento) : "Sem data"}
                    {payment.referencia && ` · Ref. ${payment.referencia}`}
                  </p>
                </div>
                <div className="flex flex-wrap items-center gap-2">
                  <Badge variant={payment.estado === "CONFIRMADO" ? "success" : payment.estado === "PENDENTE" ? "warning" : "default"}>
                    {PAGAMENTO_ESTADO_LABEL[payment.estado]}
                  </Badge>
                  {payment.estado === "PENDENTE" && (
                    <Button
                      size="sm"
                      onClick={() => confirmMutation.mutate(payment.id)}
                      disabled={confirmMutation.isPending}
                    >
                      Confirmar e emitir recibo
                    </Button>
                  )}
                </div>
              </li>
            ))}
          </ul>
        )}
      </Card>

      <Card title="Histórico de recibos">
        {receipts.length === 0 ? (
          <p className="text-sm text-slate-500">Nenhum recibo emitido para esta fatura.</p>
        ) : (
          <ul className="divide-y divide-slate-100">
            {receipts.map((receipt) => (
              <li key={receipt.id} className="flex flex-col gap-1 py-4 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <Link
                    to={`/billing/receipts/${receipt.id}`}
                    className="font-medium text-primary-700 hover:underline"
                  >
                    {receipt.numero}
                  </Link>
                  <p className="mt-1 text-sm text-slate-500">
                    {receipt.metodo_pagamento} · {formatDisplayDateTime(receipt.emitido_em)}
                  </p>
                </div>
                <div className="flex flex-col items-start gap-2 sm:items-end">
                  <p className="font-semibold text-slate-900">{formatCurrency(receipt.pagamento_valor)}</p>
                  <Link to={`/billing/receipts/${receipt.id}?imprimir=1`}>
                    <Button size="sm" variant="secondary">
                      Imprimir
                    </Button>
                  </Link>
                </div>
              </li>
            ))}
          </ul>
        )}
      </Card>
    </div>
  );
}
