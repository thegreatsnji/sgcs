import { useQuery } from "@tanstack/react-query";
import { useMemo } from "react";

import { billingService } from "@/services/billing/billing.service";
import type { Invoice } from "@/types/billing";

function isSameLocalDay(iso: string): boolean {
  const d = new Date(iso);
  const now = new Date();
  return (
    d.getFullYear() === now.getFullYear() &&
    d.getMonth() === now.getMonth() &&
    d.getDate() === now.getDate()
  );
}

function isFullyPaid(inv: Invoice): boolean {
  if (inv.estado === "PAGA") return true;
  const total = Number(inv.total);
  const paid = Number(inv.total_pago);
  return total > 0 && paid >= total;
}

function isTodayInvoice(inv: Invoice): boolean {
  return Boolean(inv.emitida_em && isSameLocalDay(inv.emitida_em));
}

/**
 * Utente só vai ao médico após pagamento integral de uma fatura emitida hoje.
 */
export function useReceptionPaymentReady(patientId: number | null) {
  const { data: invoices, isLoading: invoicesLoading } = useQuery({
    queryKey: ["billing-invoices", "payment-gate", patientId],
    queryFn: () => billingService.listInvoices({ paciente: patientId, page_size: 20 }),
    enabled: !!patientId,
    staleTime: 10_000,
  });

  const todayInvoices = useMemo(
    () => (invoices?.results ?? []).filter((inv) => inv.paciente === patientId && isTodayInvoice(inv)),
    [invoices?.results, patientId],
  );

  const partialInvoice = useMemo(
    () =>
      todayInvoices.find(
        (inv) => inv.estado !== "CANCELADA" && Number(inv.total_pago) > 0 && !isFullyPaid(inv),
      ) ?? null,
    [todayInvoices],
  );

  const paidInvoice = useMemo(
    () => todayInvoices.find((inv) => isFullyPaid(inv)) ?? null,
    [todayInvoices],
  );

  const isReady = Boolean(paidInvoice);

  return {
    isPaymentReady: isReady,
    partialInvoice,
    paidInvoice,
    isLoading: invoicesLoading,
  };
}
