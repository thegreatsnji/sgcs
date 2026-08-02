import { useQuery } from "@tanstack/react-query";
import { useParams } from "react-router-dom";

import { Button, LoadingState } from "@/design-system";
import { BillingSubNav } from "@/features/billing/components/BillingSubNav";
import { SauVidaReceiptPrint } from "@/features/billing/components/SauVidaReceiptPrint";
import { billingService } from "@/services/billing/billing.service";

export function ReceiptDetailPage() {
  const { id } = useParams<{ id: string }>();
  const receiptId = Number(id);
  const { data, isLoading } = useQuery({
    queryKey: ["billing-receipt", receiptId],
    queryFn: () => billingService.getReceipt(receiptId),
    enabled: Number.isFinite(receiptId),
  });

  if (isLoading || !data) return <LoadingState />;

  return (
    <div className="space-y-6 print:hidden-scope">
      <BillingSubNav />
      <div className="flex flex-wrap gap-2 print:hidden">
        <Button type="button" variant="secondary" onClick={() => window.print()}>
          Imprimir
        </Button>
      </div>
      <div className="print:block">
        <SauVidaReceiptPrint receiptId={receiptId} />
      </div>
    </div>
  );
}
