import { useQuery } from "@tanstack/react-query";

import { SauVidaReceiptDocument } from "@/features/billing/components/SauVidaReceiptDocument";
import { billingService } from "@/services/billing/billing.service";

export interface SauVidaReceiptPrintProps {
  receiptId: number;
  segundaVia?: boolean;
}

export function SauVidaReceiptPrint({ receiptId, segundaVia }: SauVidaReceiptPrintProps) {
  const { data, isLoading, isError } = useQuery({
    queryKey: ["receipt-print", receiptId, segundaVia],
    queryFn: () => billingService.getReceiptPrint(receiptId, segundaVia),
  });

  if (isLoading || !data) {
    return <p className="text-sm text-slate-500">A preparar recibo…</p>;
  }

  if (isError) {
    return <p className="text-sm text-red-600">Não foi possível carregar o recibo.</p>;
  }

  return <SauVidaReceiptDocument data={data} />;
}
